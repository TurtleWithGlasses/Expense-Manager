"""
Cloud Database Adapter for Expense Manager
Supports both SQLite (local) and PostgreSQL (cloud) databases
"""
import os
import sqlite3
from datetime import date, timedelta
from typing import List, Tuple
from config import config
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudDatabase:
    """Database adapter that supports both SQLite and PostgreSQL"""
    
    def __init__(self, db_type: str = "sqlite", **kwargs):
        self.db_type = db_type
        self.conn = None
        
        if db_type == "sqlite":
            self._init_sqlite()
        elif db_type == "postgresql":
            self._init_postgresql(**kwargs)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        db_path = config.get("database_path")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._migrate()
    
    def _init_postgresql(self, host, port, database, user, password):
        """Initialize PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                cursor_factory=RealDictCursor
            )
            self._migrate()
            logger.info("Successfully connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def _migrate(self):
        """Create tables if they don't exist"""
        cursor = self.conn.cursor()
        
        if self.db_type == "sqlite":
            # SQLite migrations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL CHECK(amount >= 0),
                    category_id INTEGER NOT NULL,
                    note TEXT,
                    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL CHECK(amount >= 0),
                    source TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    amount REAL NOT NULL CHECK(amount >= 0),
                    period TEXT NOT NULL DEFAULT 'Monthly',
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE
                )
            """)
        
        else:  # PostgreSQL
            # PostgreSQL migrations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    amount DECIMAL(10,2) NOT NULL CHECK(amount >= 0),
                    category_id INTEGER NOT NULL,
                    note TEXT,
                    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incomes (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL,
                    amount DECIMAL(10,2) NOT NULL CHECK(amount >= 0),
                    source VARCHAR(255) NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id SERIAL PRIMARY KEY,
                    category_id INTEGER NOT NULL,
                    amount DECIMAL(10,2) NOT NULL CHECK(amount >= 0),
                    period VARCHAR(50) NOT NULL DEFAULT 'Monthly',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE
                )
            """)
        
        self.conn.commit()
    
    def add_category(self, name: str) -> int:
        """Add a new category"""
        cursor = self.conn.cursor()
        try:
            if self.db_type == "sqlite":
                cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            else:
                cursor.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id", (name,))
                return cursor.fetchone()['id']
            return cursor.lastrowid
        except Exception as e:
            if "UNIQUE constraint failed" in str(e) or "duplicate key value" in str(e):
                raise ValueError(f"Category '{name}' already exists")
            raise
        finally:
            self.conn.commit()
    
    def all_categories(self) -> List[Tuple[int, str]]:
        """Get all categories"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY name")
        return cursor.fetchall()
    
    def add_expense(self, date: date, amount: float, category_id: int, note: str = "") -> int:
        """Add a new expense"""
        cursor = self.conn.cursor()
        try:
            if self.db_type == "sqlite":
                cursor.execute(
                    "INSERT INTO expenses (date, amount, category_id, note) VALUES (?, ?, ?, ?)",
                    (date.isoformat(), amount, category_id, note)
                )
            else:
                cursor.execute(
                    "INSERT INTO expenses (date, amount, category_id, note) VALUES (%s, %s, %s, %s) RETURNING id",
                    (date, amount, category_id, note)
                )
                return cursor.fetchone()['id']
            return cursor.lastrowid
        finally:
            self.conn.commit()
    
    def add_income(self, date: date, amount: float, source: str) -> int:
        """Add a new income"""
        cursor = self.conn.cursor()
        try:
            if self.db_type == "sqlite":
                cursor.execute(
                    "INSERT INTO incomes (date, amount, source) VALUES (?, ?, ?)",
                    (date.isoformat(), amount, source)
                )
            else:
                cursor.execute(
                    "INSERT INTO incomes (date, amount, source) VALUES (%s, %s, %s) RETURNING id",
                    (date, amount, source)
                )
                return cursor.fetchone()['id']
            return cursor.lastrowid
        finally:
            self.conn.commit()
    
    def expenses_in_range(self, start_date: date, end_date: date) -> List[Tuple]:
        """Get expenses in date range"""
        cursor = self.conn.cursor()
        if self.db_type == "sqlite":
            cursor.execute("""
                SELECT e.id, e.date, e.amount, c.name, e.note
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE e.date BETWEEN ? AND ?
                ORDER BY e.date DESC
            """, (start_date.isoformat(), end_date.isoformat()))
        else:
            cursor.execute("""
                SELECT e.id, e.date, e.amount, c.name, e.note
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE e.date BETWEEN %s AND %s
                ORDER BY e.date DESC
            """, (start_date, end_date))
        return cursor.fetchall()
    
    def incomes_in_range(self, start_date: date, end_date: date) -> List[Tuple]:
        """Get incomes in date range"""
        cursor = self.conn.cursor()
        if self.db_type == "sqlite":
            cursor.execute("""
                SELECT id, date, amount, source
                FROM incomes
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (start_date.isoformat(), end_date.isoformat()))
        else:
            cursor.execute("""
                SELECT id, date, amount, source
                FROM incomes
                WHERE date BETWEEN %s AND %s
                ORDER BY date DESC
            """, (start_date, end_date))
        return cursor.fetchall()
    
    def add_budget(self, category_name: str, amount: float, period: str = "Monthly") -> int:
        """Add or update budget for a category"""
        cursor = self.conn.cursor()
        try:
            # Get or create category
            category_id = self._get_or_create_category(category_name)
            
            if self.db_type == "sqlite":
                cursor.execute("""
                    INSERT OR REPLACE INTO budgets (id, category_id, amount, period, created_at)
                    SELECT b.id, ?, ?, ?, datetime('now')
                    FROM budgets b
                    WHERE b.category_id = ?
                    UNION ALL
                    SELECT NULL, ?, ?, ?, datetime('now')
                    WHERE NOT EXISTS (SELECT 1 FROM budgets WHERE category_id = ?)
                """, (category_id, amount, period, category_id, category_id, amount, period, category_id))
            else:
                cursor.execute("""
                    INSERT INTO budgets (category_id, amount, period)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (category_id) DO UPDATE SET
                    amount = EXCLUDED.amount,
                    period = EXCLUDED.period,
                    created_at = CURRENT_TIMESTAMP
                """, (category_id, amount, period))
            
            return category_id
        finally:
            self.conn.commit()
    
    def _get_or_create_category(self, name: str) -> int:
        """Get category ID or create if it doesn't exist"""
        cursor = self.conn.cursor()
        if self.db_type == "sqlite":
            cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return self.add_category(name)
        else:
            cursor.execute("SELECT id FROM categories WHERE name = %s", (name,))
            result = cursor.fetchone()
            if result:
                return result['id']
            else:
                return self.add_category(name)
    
    def get_budgets(self) -> List[Tuple]:
        """Get all budgets with category names"""
        cursor = self.conn.cursor()
        if self.db_type == "sqlite":
            cursor.execute("""
                SELECT b.id, c.name, b.amount, b.period
                FROM budgets b
                JOIN categories c ON b.category_id = c.id
                ORDER BY c.name
            """)
        else:
            cursor.execute("""
                SELECT b.id, c.name, b.amount, b.period
                FROM budgets b
                JOIN categories c ON b.category_id = c.id
                ORDER BY c.name
            """)
        return cursor.fetchall()
    
    def get_spent_amount(self, category_name: str, period: str) -> float:
        """Get spent amount for a category in a period"""
        cursor = self.conn.cursor()
        
        # Calculate date range based on period
        end_date = date.today()
        if period == "Weekly":
            start_date = end_date - timedelta(days=7)
        elif period == "Monthly":
            start_date = end_date - timedelta(days=30)
        elif period == "Yearly":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        if self.db_type == "sqlite":
            cursor.execute("""
                SELECT COALESCE(SUM(e.amount), 0)
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE c.name = ? AND e.date BETWEEN ? AND ?
            """, (category_name, start_date.isoformat(), end_date.isoformat()))
        else:
            cursor.execute("""
                SELECT COALESCE(SUM(e.amount), 0)
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE c.name = %s AND e.date BETWEEN %s AND %s
            """, (category_name, start_date, end_date))
        
        result = cursor.fetchone()
        return float(result[0]) if result else 0.0
    
    def delete_budget(self, category_name: str):
        """Delete budget for a category"""
        cursor = self.conn.cursor()
        if self.db_type == "sqlite":
            cursor.execute("""
                DELETE FROM budgets
                WHERE category_id = (SELECT id FROM categories WHERE name = ?)
            """, (category_name,))
        else:
            cursor.execute("""
                DELETE FROM budgets
                WHERE category_id = (SELECT id FROM categories WHERE name = %s)
            """, (category_name,))
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

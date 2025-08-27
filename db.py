import sqlite3
from datetime import date
from typing import List, Tuple, Optional

DB_FILE = "C:\\Users\\mhmts\\Documents\\Google Drive Backups\\expenses.db"

class Database:
    """SQLite data access layer for categories, expenses and incomes."""
    def __init__(self, path: str = DB_FILE) -> None:
        self.conn = sqlite3.connect(path)
        # self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self._migrate()
    
    def _migrate(self) -> None:
            c = self.conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    amount REAL NOT NULL CHECK(amount >= 0),
                    note TEXT,
                    date TEXT NOT NULL,
                    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE
                )
                """
            )
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS incomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL CHECK(amount >= 0),
                    source TEXT,
                    date TEXT NOT NULL
                )
                """
            )
            self.conn.commit()
    
    def add_category(self, name: str) -> None:
         self.conn.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name.strip(),))
         self.conn.commit()
    
    def rename_category(self, old: str, new: str) -> None:
         self.conn.execute("UPDATE categories SET name=? WHERE name=?", (new.strip(), old.strip()))
         self.conn.commit()
    
    def all_categories(self) -> List[Tuple[int, str]]:
         return self.conn.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
    
    def cat_id(self, name: str) -> Optional[int]:
        row = self.conn.execute("SELECT id FROM categories WHERE name=?", (name.strip(),)).fetchone()
        return row[0] if row else None

    # expenses
    def add_expense(self, category_name: str, amount: float, note: str, d: date) -> None:
        cid = self.cat_id(category_name)
        if cid is None:
            self.add_category(category_name)
            cid = self.cat_id(category_name)
        self.conn.execute(
             "INSERT INTO expenses(category_id, amount, note, date) VALUES (?,?,?,?)",
            (cid, float(amount), note, d.isoformat())
        )
        self.conn.commit()
    
    def update_expense(self, expense_id: int, category_name: str, amount: float, note: str, d: date) -> None:
        cid = self.cat_id(category_name)
        if cid is None:
            self.add_category(category_name)
            cid = self.cat_id(category_name)
        self.conn.execute(
            "UPDATE expenses SET category_id=?, amount=?, note=?, date=? WHERE id=?",
            (cid, float(amount), note, d.isoformat(), expense_id),
        )
        self.conn.commit()
    
    def delete_expense(self, expense_id: int) -> None:
        self.conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        self.conn.commit()
    
    def delete_category(self, name: str) -> None:
        """Deletes the category by name. Expenses are removed via ON DELETE CASCADE."""
        self.conn.execute("DELETE FROM categories WHERE name = ?", (name.strip(),))
        self.conn.commit()
    
    def sum_by_category(self, start: date, end: date) -> List[Tuple[str, float]]:
        return self.conn.execute(
            """
            SELECT c.name, COALESCE(SUM(e.amount), 0)
            FROM categories c
            LEFT JOIN expenses e ON e.category_id=c.id AND date(e.date) BETWEEN date(?) AND date(?)
            GROUP BY c.id
            ORDER BY c.name
            """,
            (start.isoformat(), end.isoformat()),
        ).fetchall()
    
    def expenses_for_category(self, category_name: str, start: date, end: date) -> List[Tuple[int, str, float, str]]:
        """Return (id, date, amount, note) for a category within range."""
        return self.conn.execute(
            """
            SELECT e.id, e.date, e.amount, COALESCE(e.note, '')
            FROM expenses e
            JOIN categories c ON c.id = e.category_id
            WHERE c.name = ? AND date(e.date) BETWEEN date(?) AND date(?)
            ORDER BY date(e.date) DESC, e.id DESC
            """,
            (category_name, start.isoformat(), end.isoformat()),
        ).fetchall()
    
    def expenses_in_range(self, start: date, end: date) -> List[Tuple[int, str, float, str, str]]:
        """Return (id, date, amount, category, note) for ALL expenses in range."""
        return self.conn.execute(
            """
            SELECT e.id, e.date, e.amount, c.name AS category, COALESCE(e.note, '')
            FROM expenses e
            JOIN categories c ON c.id = e.category_id
            WHERE date(e.date) BETWEEN date(?) AND date(?)
            ORDER BY date(e.date) DESC, e.id DESC
            """,
            (start.isoformat(), end.isoformat()),
        ).fetchall()
    
    def expenses_daily_by_category(self, start: date, end: date):
        """
        Returns rows of (date_str 'YYYY-MM-DD', category_name, total_amount)
        for each day/category in the range.
        """
        return self.conn.execute(
            """
            SELECT date(e.date) AS d, c.name AS category, COALESCE(SUM(e.amount), 0) AS total
            FROM expenses e
            JOIN categories c ON c.id = e.category_id
            WHERE date(e.date) BETWEEN date(?) AND date(?)
            GROUP BY d, c.name
            ORDER BY d, c.name
            """,
            (start.isoformat(), end.isoformat()),
        ).fetchall()
    
    def count_expenses_in_category(self, name:str) -> int:
        row = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM expenses e
            JOIN categories c ON c.id = e.category_id
            WHERE c.name = ?
            """,
            (name.strip(),),
        ).fetchone()
        return int(row[0] or 0)
    
    # incomes
    def add_income(self, amount: float, source: str, d: date) -> None:
        self.conn.execute(
            "INSERT INTO incomes(amount, source, date) VALUES (?,?,?)",
            (float(amount), source, d.isoformat()),
        )
        self.conn.commit()
    
    def update_income(self, income_id: int, amount: float, source: str, d: date) -> None:
        self.conn.execute(
            "UPDATE incomes SET amount=?, source=?, date=? WHERE id=?",
            (float(amount), source, d.isoformat(), income_id),
        )
        self.conn.commit()

    def delete_income(self, income_id: int) -> None:
        self.conn.execute("DELETE FROM incomes WHERE id=?", (income_id,))
        self.conn.commit()

    
    def incomes_in_range(self, start: date, end: date) -> List[Tuple[int, str, float, str]]:
        """Return (id, date, amount, source) for incomes in range."""
        return self.conn.execute(
            """
            SELECT id, date, amount, COALESCE(source, '')
            FROM incomes
            WHERE date(date) BETWEEN date(?) AND date(?)
            ORDER BY date(date) DESC, id DESC
            """,
            (start.isoformat(), end.isoformat()),
        ).fetchall()

    # -- totals -----------------------------------------------------------
    def total_expenses(self, start: date, end: date) -> float:
        row = self.conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM expenses WHERE date(date) BETWEEN date(?) AND date(?)",
            (start.isoformat(), end.isoformat()),
        ).fetchone()
        return float(row[0] or 0)

    def total_incomes(self, start: date, end: date) -> float:
        row = self.conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM incomes WHERE date(date) BETWEEN date(?) AND date(?)",
            (start.isoformat(), end.isoformat()),
        ).fetchone()
        return float(row[0] or 0)

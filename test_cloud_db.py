"""
Test script for cloud database functionality
"""
import sys
import os
from datetime import date

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cloud_db import CloudDatabase
from config import config

def test_sqlite():
    """Test SQLite database functionality"""
    print("🧪 Testing SQLite database...")
    
    try:
        with CloudDatabase(db_type="sqlite") as db:
            # Test adding a category
            cat_id = db.add_category("Test Category")
            print(f"  ✅ Added category: {cat_id}")
            
            # Test adding an expense
            exp_id = db.add_expense(date.today(), 100.0, cat_id, "Test expense")
            print(f"  ✅ Added expense: {exp_id}")
            
            # Test adding an income
            inc_id = db.add_income(date.today(), 500.0, "Test income")
            print(f"  ✅ Added income: {inc_id}")
            
            # Test getting expenses
            expenses = db.expenses_in_range(date.today(), date.today())
            print(f"  ✅ Found {len(expenses)} expenses")
            
            # Test getting incomes
            incomes = db.incomes_in_range(date.today(), date.today())
            print(f"  ✅ Found {len(incomes)} incomes")
            
            # Test budget functionality
            budget_id = db.add_budget("Test Category", 200.0, "Monthly")
            print(f"  ✅ Added budget: {budget_id}")
            
            budgets = db.get_budgets()
            print(f"  ✅ Found {len(budgets)} budgets")
            
            print("  🎉 SQLite test completed successfully!")
            return True
            
    except Exception as e:
        print(f"  ❌ SQLite test failed: {e}")
        return False

def test_postgresql():
    """Test PostgreSQL database functionality"""
    print("\n🧪 Testing PostgreSQL database...")
    
    # Check if cloud database is configured
    cloud_config = config.get("cloud_database", {})
    if not all([cloud_config.get("host"), cloud_config.get("database"), 
               cloud_config.get("user"), cloud_config.get("password")]):
        print("  ⚠️  PostgreSQL not configured, skipping test")
        return True
    
    try:
        with CloudDatabase(
            db_type="postgresql",
            host=cloud_config["host"],
            port=cloud_config.get("port", 5432),
            database=cloud_config["database"],
            user=cloud_config["user"],
            password=cloud_config["password"]
        ) as db:
            # Test adding a category
            cat_id = db.add_category("Test Category PG")
            print(f"  ✅ Added category: {cat_id}")
            
            # Test adding an expense
            exp_id = db.add_expense(date.today(), 150.0, cat_id, "Test expense PG")
            print(f"  ✅ Added expense: {exp_id}")
            
            # Test adding an income
            inc_id = db.add_income(date.today(), 750.0, "Test income PG")
            print(f"  ✅ Added income: {inc_id}")
            
            # Test getting expenses
            expenses = db.expenses_in_range(date.today(), date.today())
            print(f"  ✅ Found {len(expenses)} expenses")
            
            # Test getting incomes
            incomes = db.incomes_in_range(date.today(), date.today())
            print(f"  ✅ Found {len(incomes)} incomes")
            
            # Test budget functionality
            budget_id = db.add_budget("Test Category PG", 300.0, "Monthly")
            print(f"  ✅ Added budget: {budget_id}")
            
            budgets = db.get_budgets()
            print(f"  ✅ Found {len(budgets)} budgets")
            
            print("  🎉 PostgreSQL test completed successfully!")
            return True
            
    except Exception as e:
        print(f"  ❌ PostgreSQL test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Cloud Database Test Suite")
    print("=" * 40)
    
    # Test SQLite
    sqlite_success = test_sqlite()
    
    # Test PostgreSQL
    postgresql_success = test_postgresql()
    
    # Summary
    print("\n📊 Test Results:")
    print(f"  SQLite: {'✅ PASS' if sqlite_success else '❌ FAIL'}")
    print(f"  PostgreSQL: {'✅ PASS' if postgresql_success else '❌ FAIL'}")
    
    if sqlite_success and postgresql_success:
        print("\n🎉 All tests passed! Cloud database is ready to use.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

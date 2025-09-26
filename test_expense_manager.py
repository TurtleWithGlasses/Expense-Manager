"""
Simple tests for Expense Manager
"""
import unittest
import tempfile
import os
from datetime import date
from db import Database

class TestExpenseManager(unittest.TestCase):
    """Test cases for Expense Manager functionality"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        os.unlink(self.temp_db.name)
    
    def test_add_category(self):
        """Test adding a category"""
        self.db.add_category("Test Category")
        categories = self.db.all_categories()
        self.assertTrue(any(name == "Test Category" for _, name in categories))
    
    def test_add_expense(self):
        """Test adding an expense"""
        self.db.add_category("Food")
        self.db.add_expense("Food", 25.50, "Lunch", date.today())
        
        # Check if expense was added
        expenses = self.db.expenses_in_range(date.today(), date.today())
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0][2], 25.50)  # amount
        self.assertEqual(expenses[0][3], "Food")  # category
    
    def test_add_income(self):
        """Test adding income"""
        self.db.add_income(1000.0, "Salary", date.today())
        
        # Check if income was added
        incomes = self.db.incomes_in_range(date.today(), date.today())
        self.assertEqual(len(incomes), 1)
        self.assertEqual(incomes[0][2], 1000.0)  # amount
        self.assertEqual(incomes[0][3], "Salary")  # source
    
    def test_budget_management(self):
        """Test budget management"""
        self.db.add_category("Food")
        self.db.add_budget("Food", 500.0, "Monthly")
        
        budget = self.db.get_budget("Food")
        self.assertIsNotNone(budget)
        self.assertEqual(budget[1], 500.0)  # amount
        self.assertEqual(budget[2], "Monthly")  # period
    
    def test_category_totals(self):
        """Test category totals calculation"""
        self.db.add_category("Food")
        self.db.add_category("Transport")
        
        # Add some expenses
        self.db.add_expense("Food", 50.0, "Groceries", date.today())
        self.db.add_expense("Food", 25.0, "Restaurant", date.today())
        self.db.add_expense("Transport", 30.0, "Bus", date.today())
        
        totals = self.db.sum_by_category(date.today(), date.today())
        food_total = next((amount for name, amount in totals if name == "Food"), 0)
        transport_total = next((amount for name, amount in totals if name == "Transport"), 0)
        
        self.assertEqual(food_total, 75.0)
        self.assertEqual(transport_total, 30.0)
    
    def test_total_calculations(self):
        """Test total income and expense calculations"""
        # Add some data
        self.db.add_income(1000.0, "Salary", date.today())
        self.db.add_income(200.0, "Freelance", date.today())
        
        self.db.add_category("Food")
        self.db.add_expense("Food", 100.0, "Groceries", date.today())
        self.db.add_expense("Food", 50.0, "Restaurant", date.today())
        
        total_income = self.db.total_incomes(date.today(), date.today())
        total_expenses = self.db.total_expenses(date.today(), date.today())
        
        self.assertEqual(total_income, 1200.0)
        self.assertEqual(total_expenses, 150.0)

if __name__ == '__main__':
    unittest.main()

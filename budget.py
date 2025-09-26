"""
Budget tracking and management for Expense Manager
"""
from datetime import date, timedelta
from typing import List, Tuple, Dict, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QFormLayout, QLineEdit, QComboBox, QDateEdit, 
    QDialogButtonBox, QMessageBox, QProgressBar, QWidget
)
from PySide6.QtCore import QDate, Qt, QTimer
from PySide6.QtGui import QFont, QColor
from db import Database

class BudgetDialog(QDialog):
    """Dialog for managing budgets"""
    
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Budget Management")
        self.setModal(True)
        self.resize(600, 400)
        
        self.setup_ui()
        self.load_budgets()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Budget Management")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        header.addWidget(title)
        header.addStretch()
        
        self.btn_add = QPushButton("Add Budget")
        self.btn_edit = QPushButton("Edit Budget")
        self.btn_delete = QPushButton("Delete Budget")
        self.btn_add.clicked.connect(self.add_budget)
        self.btn_edit.clicked.connect(self.edit_budget)
        self.btn_delete.clicked.connect(self.delete_budget)
        
        header.addWidget(self.btn_add)
        header.addWidget(self.btn_edit)
        header.addWidget(self.btn_delete)
        layout.addLayout(header)
        
        # Budget table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Category", "Budget Amount", "Spent", "Remaining", "Progress"
        ])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemDoubleClicked.connect(self.edit_budget)
        layout.addWidget(self.table)
        
        # Summary
        self.summary_label = QLabel()
        self.summary_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.summary_label)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)
    
    def load_budgets(self):
        """Load and display budgets"""
        budgets = self.db.get_budgets()
        self.table.setRowCount(len(budgets))
        
        total_budget = 0
        total_spent = 0
        
        for row, (cat_id, category, amount, period) in enumerate(budgets):
            # Calculate spent amount for this period
            spent = self.db.get_spent_amount(category, period)
            remaining = amount - spent
            progress = (spent / amount * 100) if amount > 0 else 0
            
            self.table.setItem(row, 0, QTableWidgetItem(category))
            self.table.setItem(row, 1, QTableWidgetItem(f"{amount:.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{spent:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{remaining:.2f}"))
            
            # Progress bar
            progress_widget = self.create_progress_widget(progress, remaining < 0)
            self.table.setCellWidget(row, 4, progress_widget)
            
            total_budget += amount
            total_spent += spent
        
        # Update summary
        total_remaining = total_budget - total_spent
        self.summary_label.setText(
            f"Total Budget: {total_budget:.2f} | Total Spent: {total_spent:.2f} | "
            f"Remaining: {total_remaining:.2f}"
        )
        
        self.table.resizeColumnsToContents()
    
    def create_progress_widget(self, progress: float, over_budget: bool) -> QWidget:
        """Create a progress bar widget"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(int(progress))
        
        if over_budget:
            progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff4444; }")
        elif progress > 80:
            progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #ffaa00; }")
        else:
            progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #44ff44; }")
        
        layout.addWidget(progress_bar)
        return widget
    
    def add_budget(self):
        """Add new budget"""
        dialog = BudgetEditDialog(self.db, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_budgets()
    
    def edit_budget(self):
        """Edit selected budget"""
        row = self.table.currentRow()
        if row < 0:
            return
        
        category = self.table.item(row, 0).text()
        dialog = BudgetEditDialog(self.db, self, category)
        if dialog.exec() == QDialog.Accepted:
            self.load_budgets()
    
    def delete_budget(self):
        """Delete selected budget"""
        row = self.table.currentRow()
        if row < 0:
            return
        
        category = self.table.item(row, 0).text()
        if QMessageBox.question(self, "Delete Budget", 
                              f"Delete budget for {category}?",
                              QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.delete_budget(category)
            self.load_budgets()

class BudgetEditDialog(QDialog):
    """Dialog for adding/editing individual budgets"""
    
    def __init__(self, db: Database, parent=None, category: str = None):
        super().__init__(parent)
        self.db = db
        self.category = category
        self.setWindowTitle("Edit Budget" if category else "Add Budget")
        self.setModal(True)
        
        self.setup_ui()
        if category:
            self.load_budget_data()
    
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # Category selection
        self.category_combo = QComboBox()
        categories = [name for _, name in self.db.all_categories()]
        self.category_combo.addItems(categories)
        if self.category:
            self.category_combo.setCurrentText(self.category)
            self.category_combo.setEnabled(False)  # Can't change category when editing
        layout.addRow("Category:", self.category_combo)
        
        # Budget amount
        self.amount_edit = QLineEdit()
        self.amount_edit.setPlaceholderText("Enter budget amount")
        layout.addRow("Budget Amount:", self.amount_edit)
        
        # Budget period
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Monthly", "Weekly", "Yearly"])
        layout.addRow("Period:", self.period_combo)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_budget)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def load_budget_data(self):
        """Load existing budget data for editing"""
        if not self.category:
            return
        
        budget = self.db.get_budget(self.category)
        if budget:
            self.amount_edit.setText(str(budget[1]))
            self.period_combo.setCurrentText(budget[2])
    
    def save_budget(self):
        """Save budget data"""
        category = self.category_combo.currentText()
        if not category:
            QMessageBox.warning(self, "Error", "Please select a category")
            return
        
        try:
            amount = float(self.amount_edit.text())
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid amount: {e}")
            return
        
        period = self.period_combo.currentText()
        
        if self.category:  # Editing existing budget
            self.db.update_budget(category, amount, period)
        else:  # Adding new budget
            self.db.add_budget(category, amount, period)
        
        self.accept()

class BudgetAlerts:
    """Handle budget alerts and notifications"""
    
    def __init__(self, db: Database):
        self.db = db
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_budgets)
        self.timer.start(300000)  # Check every 5 minutes
    
    def check_budgets(self):
        """Check all budgets and show alerts if needed"""
        budgets = self.db.get_budgets()
        current_date = date.today()
        
        for cat_id, category, amount, period in budgets:
            spent = self.db.get_spent_amount(category, period)
            remaining = amount - spent
            progress = (spent / amount * 100) if amount > 0 else 0
            
            # Alert if over budget
            if remaining < 0:
                self.show_alert(f"Budget Alert: {category} is over budget by {abs(remaining):.2f}")
            # Alert if close to budget limit (90% or more)
            elif progress >= 90:
                self.show_alert(f"Budget Warning: {category} is at {progress:.1f}% of budget")
    
    def show_alert(self, message: str):
        """Show budget alert (placeholder - could be system notification)"""
        print(f"BUDGET ALERT: {message}")  # In a real app, this would be a system notification

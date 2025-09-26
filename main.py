from datetime import date, timedelta

from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QFont, QIcon, QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QDateEdit, QGridLayout, QInputDialog, QMessageBox, QScrollArea,
    QComboBox, QMenuBar, QMenu, QDialog
)
from updater import check_for_updates
from version import __version__

from db import Database
from dialogs import (
    IncomeDialog, ExpenseDialog,
    CategoryExpensesDialog, IncomesListDialog, ExpensesListDialog, ChartDialog,
    DailyExpensesChartDialog
)
from budget import BudgetDialog
from export import ExportManager
from settings import SettingsDialog
from backup import BackupManager
from widgets import CategoryCard, StatBox
from pathlib import Path
import sys

def resource_path(relative: str) -> str:
    # Works in dev and inside PyInstaller onefile
    base = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return str(Path(base) / relative)

ICON_FILE = resource_path("money_icon.png")

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense Manager — Dashboard")
        self.resize(720, 900)
        self.setWindowIcon(QIcon(ICON_FILE))

        menubar = self.menuBar() if hasattr(self, "menuBar") else QMenuBar(self)
        
        # File menu
        file_menu = menubar.addMenu("File")
        act_export = QAction("Export Data...", self)
        act_export.triggered.connect(self.export_data)
        file_menu.addAction(act_export)
        file_menu.addSeparator()
        act_backup = QAction("Create Backup...", self)
        act_backup.triggered.connect(self.create_backup)
        file_menu.addAction(act_backup)
        act_restore = QAction("Restore from Backup...", self)
        act_restore.triggered.connect(self.restore_backup)
        file_menu.addAction(act_restore)
        file_menu.addSeparator()
        act_settings = QAction("Settings...", self)
        act_settings.triggered.connect(self.open_settings)
        file_menu.addAction(act_settings)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        act_budget = QAction("Budget Management...", self)
        act_budget.triggered.connect(self.open_budget_manager)
        tools_menu.addAction(act_budget)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        act_check = QAction(f"Check for updates... (v{__version__})", self)
        act_check.triggered.connect(lambda: check_for_updates(parent=self, silent=False))
        help_menu.addAction(act_check)

        # Optional: auto-check once, 2s after launch (quiet)
        QTimer.singleShot(2000, lambda: check_for_updates(parent=self, silent=True))

        self.db = Database()
        self._seed_defaults()

        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setSpacing(14)

        # ---- Period quick buttons ----
        period_row = QHBoxLayout()
        self.btn_month = QPushButton("Month")
        self.btn_week = QPushButton("Week")
        self.btn_day = QPushButton("Day")
        for b in (self.btn_month, self.btn_week, self.btn_day):
            b.clicked.connect(self.on_period_click)
            b.setFixedHeight(36)
            b.setStyleSheet("border:1px solid #999;border-radius:10px;padding:4px 10px;")
            period_row.addWidget(b)
        period_row.addStretch()
        outer.addLayout(period_row)

        # ---- Date range ----
        range_row = QHBoxLayout()
        self.start = QDateEdit(calendarPopup=True)
        self.end = QDateEdit(calendarPopup=True)
        for ed in (self.start, self.end):
            ed.setDisplayFormat("yyyy-MM-dd")
        range_row.addWidget(QLabel("Start date"))
        range_row.addWidget(self.start)
        range_row.addWidget(QLabel(" - End date"))
        range_row.addWidget(self.end)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.refresh)
        range_row.addWidget(apply_btn)
        outer.addLayout(range_row)

        # ---- Income / Expense buttons ----
        money_row = QHBoxLayout()
        self.btn_income = QPushButton("Income")
        self.btn_expense = QPushButton("Expense")
        for w in (self.btn_income, self.btn_expense):
            w.setFixedHeight(44)
            w.setStyleSheet("border:2px solid #d33; color:#d33; border-radius:12px; font-weight:700;")
            money_row.addWidget(w)
        self.btn_income.clicked.connect(self.add_income)
        self.btn_expense.clicked.connect(self.add_expense)
        outer.addLayout(money_row)

        # ---- NEW: Totals boxes (clickable) ----
        stats_row = QHBoxLayout()
        self.box_income = StatBox("Total Income", color="#1769aa")
        self.box_expense = StatBox("Total Expenses", color="#b00020")
        self.box_income.clicked.connect(self.show_all_incomes)
        self.box_expense.clicked.connect(self.show_all_expenses)
        stats_row.addWidget(self.box_income)
        stats_row.addWidget(self.box_expense)
        outer.addLayout(stats_row)

        # ---- Balance box ----
        self.balance_box = QLabel("")
        self.balance_box.setAlignment(Qt.AlignCenter)
        self.balance_box.setMinimumHeight(90)
        f = QFont(); f.setPointSize(15); f.setBold(True)
        self.balance_box.setFont(f)
        self.balance_box.setTextFormat(Qt.RichText)
        outer.addWidget(self.balance_box)
        
        # ---- Budget status box ----
        self.budget_status_box = QLabel("")
        self.budget_status_box.setAlignment(Qt.AlignCenter)
        self.budget_status_box.setMinimumHeight(60)
        f2 = QFont(); f2.setPointSize(12); f2.setBold(True)
        self.budget_status_box.setFont(f2)
        self.budget_status_box.setTextFormat(Qt.RichText)
        outer.addWidget(self.budget_status_box)

        # ---- Categories row + action buttons ----
        header_row = QHBoxLayout()
        title = QLabel("Categories")
        title.setStyleSheet("font-weight:700;")
        header_row.addWidget(title)
        header_row.addStretch()
        self.btn_add_cat = QPushButton("Add Category")
        self.btn_edit_cat = QPushButton("Edit Category")
        for w in (self.btn_add_cat, self.btn_edit_cat):
            w.setFixedHeight(32)
            w.setStyleSheet("border:1px solid #999; border-radius:8px; padding:4px 10px; font-weight:600;")
            header_row.addWidget(w)
        self.btn_add_cat.clicked.connect(self.add_category)
        self.btn_edit_cat.clicked.connect(self.edit_category)
        outer.addLayout(header_row)

        # ---- Scrollable grid of category cards ----
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.cards_host = QWidget()
        self.grid = QGridLayout(self.cards_host)
        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(12)
        self.scroll.setWidget(self.cards_host)
        outer.addWidget(self.scroll, 1)

        self.dataset_sel = QComboBox()
        self.dataset_sel.addItems(["Expenses by Category", "Incomes by Source"])
        self.btn_pie = QPushButton("Pie")
        self.btn_bar = QPushButton("Bars")
        self.btn_daily = QPushButton("Daily")
        self.btn_pie.clicked.connect(self.open_pie_chart)
        self.btn_bar.clicked.connect(self.open_bar_chart)
        self.btn_daily.clicked.connect(self.open_daily_cart)
        self.btn_del_cat = QPushButton("Delete Category")
        self.btn_del_cat.setFixedHeight(32)
        self.btn_del_cat.setStyleSheet("border:1px solid #999; border-radius:8px; padding:4px 10px; font-weight:600;")
        self.btn_del_cat.clicked.connect(self.delete_category)
        header_row.addWidget(self.btn_del_cat)

        header_row.addSpacing(8)
        header_row.addWidget(QLabel("Chart:"))
        header_row.addWidget(self.dataset_sel)
        header_row.addWidget(self.btn_pie)
        header_row.addWidget(self.btn_bar)
        header_row.addWidget(self.btn_daily)

        # Defaults and initial load
        self._set_default_range()
        self.refresh()

    # ------------------------ helpers & actions ------------------------ #
    def _seed_defaults(self):
        for name in ["Food", "Other"]:
            self.db.add_category(name)

    def _set_default_range(self):
        today = date.today()
        first = today.replace(day=1)
        self.start.setDate(QDate(first.year, first.month, first.day))
        self.end.setDate(QDate(today.year, today.month, today.day))

    def current_range(self):
        s = self.start.date().toPython()
        e = self.end.date().toPython()
        if s > e:
            s, e = e, s
        return s, e

    def on_period_click(self):
        sender = self.sender()
        today = date.today()
        if sender is self.btn_month:
            start = today.replace(day=1)
        elif sender is self.btn_week:
            start = today - timedelta(days=6)
        else:  # day
            start = today
        self.start.setDate(QDate(start.year, start.month, start.day))
        self.end.setDate(QDate(today.year, today.month, today.day))
        self.refresh()

    # ---- income & expense dialogs ----
    def add_income(self):
        dlg = IncomeDialog(self)
        result = dlg.get()
        if result:
            d, amount, src = result
            self.db.add_income(amount, src, d)
            self.refresh()

    def add_expense(self):
        cats = [name for (_id, name) in self.db.all_categories()]
        dlg = ExpenseDialog(cats, self)
        result = dlg.get()
        if result:
            d, cat, amount, note = result
            if not cat:
                QMessageBox.information(self, "Category", "Please enter a category name")
                return
            self.db.add_expense(cat, amount, note, d)
            self.refresh()

    # ---- categories ----
    def add_category(self):
        name, ok = QInputDialog.getText(self, "Add category", "Name:")
        if ok and name.strip():
            self.db.add_category(name)
            self.refresh()

    def edit_category(self):
        cats = [name for (_id, name) in self.db.all_categories()]
        if not cats:
            return
        old, ok = QInputDialog.getItem(self, "Edit category", "Select:", cats, 0, False)
        if not ok:
            return
        new, ok2 = QInputDialog.getText(self, "Rename", f"New name for '{old}':")
        if ok2 and new.strip():
            try:
                self.db.rename_category(old, new)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
            self.refresh()
    
    def delete_category(self):
        cats = [name for (_id, name) in self.db.all_categories()]
        if not cats:
            return
        name, ok = QInputDialog.getItem(self, "Delete category", "Select:", cats, 0, False)
        if not ok:
            return
        
        n = self.db.count_expenses_in_category(name)
        msg = (f"Delete category '{name}'?\n\n"
               f"This will also delete {n} expense(s) in this category.")
        if QMessageBox.question(self, "Confirm delete", msg,
                                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        
        self.db.delete_category(name)
        self.refresh()

    # ---- refresh UI ----
    def refresh(self):
        self._update_stats()
        self._populate_cards()

    def _update_stats(self):
        s, e = self.current_range()
        total_inc = self.db.total_incomes(s, e)
        total_exp = self.db.total_expenses(s, e)
        self.box_income.set_amount(total_inc)
        self.box_expense.set_amount(total_exp)
        bal = total_inc - total_exp
        self.balance_box.setText(
            f"<div>Balance<br><span style='font-size:18pt'>{bal:,.2f}</span></div>"
        )
        if bal >= 0:
            self.balance_box.setStyleSheet(
                "border:2px solid #2f8a00; color:#2f8a00; border-radius:16px; padding:12px; font-weight:700;"
            )
        else:
            self.balance_box.setStyleSheet(
                "border:2px solid #b00020; color:#b00020; border-radius:16px; padding:12px; font-weight:700;"
            )
        
        # Update budget status
        self._update_budget_status()

    def _populate_cards(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        s, e = self.current_range()
        data = self.db.sum_by_category(s, e)
        cols = 3
        for i, (name, total) in enumerate(data):
            r, c = divmod(i, cols)
            card = CategoryCard(name, total)
            card.clicked.connect(lambda _=False, n=name: self.show_category_details(n))
            self.grid.addWidget(card, r, c)

    # ---- click handlers for totals boxes ----
    def show_all_incomes(self):
        s, e = self.current_range()
        dlg = IncomesListDialog(self.db, s, e, self)
        dlg.exec()
        self.refresh()  # reflect edits/deletes


    def show_all_expenses(self):
        s, e = self.current_range()
        rows = self.db.expenses_in_range(s, e)
        ExpensesListDialog(rows, self).exec()

    def show_category_details(self, category_name: str):
        s, e = self.current_range()
        dlg = CategoryExpensesDialog(self.db, category_name, s, e, self)
        dlg.exec()
        self.refresh()
    
    # --- dataset helpers ---
    def _category_totals(self):
        """Expenses by category for current period (labels, values)."""
        s, e = self.current_range()
        rows = self.db.sum_by_category(s, e)  # [(name, total)]
        labels = [n for (n, t) in rows if (t or 0) > 0]
        values = [t for (n, t) in rows if (t or 0) > 0]
        return labels, values

    def _income_totals_by_source(self):
        """Incomes grouped by 'source' for current period (labels, values)."""
        from collections import defaultdict
        s, e = self.current_range()
        rows = self.db.incomes_in_range(s, e)  # [(id, date, amount, source)]
        agg = defaultdict(float)
        for (_id, _d, amt, src) in rows:
            key = src.strip() if src and src.strip() else "Income"
            agg[key] += float(amt or 0)
        labels = list(agg.keys())
        values = [agg[k] for k in labels]
        return labels, values

    def _selected_dataset(self):
        return "expenses" if self.dataset_sel.currentIndex() == 0 else "incomes"

    # --- chart launchers ---
    def open_pie_chart(self):
        ds = self._selected_dataset()
        if ds == "expenses":
            labels, values = self._category_totals()
            title = "Expenses by Category (%)"
        else:
            labels, values = self._income_totals_by_source()
            title = "Incomes by Source (%)"
        ChartDialog(title, labels, values, chart="pie", parent=self).exec()

    def open_bar_chart(self):
        ds = self._selected_dataset()
        if ds == "expenses":
            labels, values = self._category_totals()
            title = "Expenses by Category (Total)"
        else:
            labels, values = self._income_totals_by_source()
            title = "Incomes by Source (Total)"
        ChartDialog(title, labels, values, chart="bar", parent=self).exec()

    def _daily_expense_pivot(self):
        """Return (dates[], {category: [values aligned to dates]}) for current range."""
        s, e = self.current_range()
        rows = self.db.expenses_daily_by_category(s, e) # (d, cat, total)
        dates = sorted({d for (d, _cat, _t) in rows})
        cats = sorted({cat for (_d, cat, _t) in rows})
        idx = {d: i for i, d in enumerate(dates)}
        series = {cat: [0.0] * len(dates) for cat in cats}
        for d, cat, total in rows:
            series[cat][idx[d]] = float(total or 0)
        return dates, series
    
    def open_daily_cart(self):
        dates, series = self._daily_expense_pivot()
        DailyExpensesChartDialog(dates, series, self).exec()
    
    def export_data(self):
        """Export data using the export manager"""
        s, e = self.current_range()
        export_manager = ExportManager(self)
        export_manager.export_data(self.db, s, e)
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Refresh the UI if needed
            self.refresh()
    
    def open_budget_manager(self):
        """Open budget management dialog"""
        dialog = BudgetDialog(self.db, self)
        dialog.exec()
        # Refresh to show any budget-related changes
        self.refresh()
    
    def create_backup(self):
        """Create a database backup"""
        from config import config
        db_path = config.get("database_path")
        backup_manager = BackupManager(self)
        backup_manager.create_backup(db_path)
    
    def restore_backup(self):
        """Restore database from backup"""
        from config import config
        db_path = config.get("database_path")
        backup_manager = BackupManager(self)
        backup_manager.restore_backup(db_path)
        # Refresh the UI after restore
        self.refresh()
    
    def _update_budget_status(self):
        """Update budget status display"""
        try:
            budgets = self.db.get_budgets()
            if not budgets:
                self.budget_status_box.setText("No budgets set")
                self.budget_status_box.setStyleSheet(
                    "border:1px solid #999; color:#666; border-radius:8px; padding:8px;"
                )
                return
            
            over_budget_count = 0
            warning_count = 0
            total_budget = 0
            total_spent = 0
            
            for cat_id, category, amount, period in budgets:
                spent = self.db.get_spent_amount(category, period)
                total_budget += amount
                total_spent += spent
                
                if spent > amount:
                    over_budget_count += 1
                elif spent / amount >= 0.8:  # 80% or more
                    warning_count += 1
            
            if over_budget_count > 0:
                status_text = f"⚠️ {over_budget_count} category(ies) over budget"
                color = "#b00020"
            elif warning_count > 0:
                status_text = f"⚠️ {warning_count} category(ies) near budget limit"
                color = "#ffaa00"
            else:
                status_text = f"✅ Budget status: {total_spent:.0f}/{total_budget:.0f} spent"
                color = "#2f8a00"
            
            self.budget_status_box.setText(status_text)
            self.budget_status_box.setStyleSheet(
                f"border:2px solid {color}; color:{color}; border-radius:8px; padding:8px;"
            )
            
        except Exception as e:
            self.budget_status_box.setText("Budget status unavailable")
            self.budget_status_box.setStyleSheet(
                "border:1px solid #999; color:#666; border-radius:8px; padding:8px;"
            )

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    w = Dashboard()
    w.setWindowIcon(QIcon(ICON_FILE))
    w.show()
    return app.exec()

if __name__ == "__main__":
    import sys
    sys.exit(main())
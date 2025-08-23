from typing import List, Optional
from datetime import date
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QDialogButtonBox, QDateEdit, QLineEdit, QComboBox, QMessageBox,
    QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton
)
from PySide6.QtCore import QDate, Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
# ---------------------- Add dialogs ---------------------- #
class IncomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Income")
        self.setModal(True)
        lay = QFormLayout(self)
        self.date = QDateEdit(calendarPopup=True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setDate(QDate.currentDate())
        self.amount = QLineEdit()
        self.source = QLineEdit()
        lay.addRow("Date", self.date)
        lay.addRow("Amount", self.amount)
        lay.addRow("Source", self.source)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addRow(btns)

    def get(self):
        if self.exec() == QDialog.Accepted:
            try:
                amt = float(self.amount.text())
            except ValueError:
                QMessageBox.warning(self, "Invalid", "Amount must be a number")
                return None
            return (self.date.date().toPython(), amt, self.source.text().strip())
        return None


class ExpenseDialog(QDialog):
    def __init__(self, categories: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Expense")
        self.setModal(True)
        lay = QFormLayout(self)
        self.date = QDateEdit(calendarPopup=True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setDate(QDate.currentDate())

        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.addItems(categories)
        if categories:
            self.category.setCurrentIndex(0)

        self.amount = QLineEdit()
        self.note = QLineEdit()

        lay.addRow("Date", self.date)
        lay.addRow("Category", self.category)
        lay.addRow("Amount", self.amount)
        lay.addRow("Note", self.note)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addRow(btns)

    def get(self):
        if self.exec() == QDialog.Accepted:
            try:
                amt = float(self.amount.text())
            except ValueError:
                QMessageBox.warning(self, "Invalid", "Amount must be a number")
                return None
            return (
                self.date.date().toPython(),
                self.category.currentText().strip(),
                amt,
                self.note.text().strip(),
            )
        return None


# ---------------- Category detail (edit/delete) ---------------- #
class EditExpenseDialog(QDialog):
    def __init__(self, categories: List[str], init_date: date, init_category: str, init_amount: float, init_note: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Expense")
        lay = QFormLayout(self)
        self.date = QDateEdit(calendarPopup=True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setDate(QDate(init_date.year, init_date.month, init_date.day))

        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.addItems(categories)
        if init_category in categories:
            self.category.setCurrentText(init_category)
        else:
            self.category.setEditText(init_category)

        self.amount = QLineEdit(str(init_amount))
        self.note = QLineEdit(init_note)

        lay.addRow("Date", self.date)
        lay.addRow("Category", self.category)
        lay.addRow("Amount", self.amount)
        lay.addRow("Note", self.note)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addRow(btns)

    def get(self):
        if self.exec() == QDialog.Accepted:
            try:
                amt = float(self.amount.text())
            except ValueError:
                QMessageBox.warning(self, "Invalid", "Amount must be a number")
                return None
            return (
                self.date.date().toPython(),
                self.category.currentText().strip(),
                amt,
                self.note.text().strip(),
            )
        return None


class CategoryExpensesDialog(QDialog):
    """Table showing expenses for a category in a period, with edit/delete."""
    def __init__(self, db, category_name: str, start: date, end: date, parent=None):
        super().__init__(parent)
        self.db = db
        self.category_name = category_name
        self.setWindowTitle(f"{category_name} — Expenses")

        outer = QVBoxLayout(self)

        # Top row: date range within dialog
        top = QHBoxLayout()
        self.start = QDateEdit(calendarPopup=True)
        self.end = QDateEdit(calendarPopup=True)
        self.start.setDisplayFormat("yyyy-MM-dd")
        self.end.setDisplayFormat("yyyy-MM-dd")
        self.start.setDate(QDate(start.year, start.month, start.day))
        self.end.setDate(QDate(end.year, end.month, end.day))
        apply = QPushButton("Apply")
        apply.clicked.connect(self.reload)
        top.addWidget(QLabel("Start")); top.addWidget(self.start)
        top.addWidget(QLabel("End")); top.addWidget(self.end)
        top.addWidget(apply)
        outer.addLayout(top)

        self.lbl_info = QLabel("")
        outer.addWidget(self.lbl_info)

        # Table: Date, Amount, Note, (hidden ID)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Date", "Amount", "Note", "ID"])
        self.table.setColumnHidden(3, True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        outer.addWidget(self.table)

        # Bottom controls
        controls = QHBoxLayout()
        self.btn_edit = QPushButton("Edit Selected")
        self.btn_delete = QPushButton("Delete Selected")
        self.btn_close = QPushButton("Close")
        self.btn_edit.clicked.connect(self.edit_selected)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_close.clicked.connect(self.reject)
        controls.addWidget(self.btn_edit)
        controls.addWidget(self.btn_delete)
        controls.addStretch()
        controls.addWidget(self.btn_close)
        outer.addLayout(controls)

        # Footer total
        self.lbl_total = QLabel("Total: 0.00")
        self.lbl_total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        outer.addWidget(self.lbl_total)

        self.reload()

    def _current_range(self):
        s = self.start.date().toPython()
        e = self.end.date().toPython()
        if s > e:
            s, e = e, s
        return s, e

    def reload(self):
        s, e = self._current_range()
        rows = self.db.expenses_for_category(self.category_name, s, e)
        self.table.setRowCount(0)
        total = 0.0
        for (exp_id, dstr, amt, note) in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(dstr))
            amt_item = QTableWidgetItem(f"{amt:.2f}")
            amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(r, 1, amt_item)
            self.table.setItem(r, 2, QTableWidgetItem(note))
            self.table.setItem(r, 3, QTableWidgetItem(str(exp_id)))
            total += float(amt or 0)

        self.table.resizeColumnsToContents()
        self.lbl_total.setText(f"Total: {total:.2f}")
        self.lbl_info.setText(f"{self.category_name} — {len(rows)} items")

    def _selected_id(self) -> Optional[int]:
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 3).text())

    def edit_selected(self):
        exp_id = self._selected_id()
        if exp_id is None:
            return
        row = self.table.currentRow()
        cur_date = date.fromisoformat(self.table.item(row, 0).text())
        cur_amount = float(self.table.item(row, 1).text())
        cur_note = self.table.item(row, 2).text() or ""
        cur_cat = self.category_name

        cats = [name for (_id, name) in self.db.all_categories()]
        dlg = EditExpenseDialog(cats, cur_date, cur_cat, cur_amount, cur_note, self)
        res = dlg.get()
        if res:
            d, new_cat, amount, note = res
            self.db.update_expense(exp_id, new_cat, amount, note, d)
            self.reload()

    def delete_selected(self):
        exp_id = self._selected_id()
        if exp_id is None:
            return
        from PySide6.QtWidgets import QMessageBox
        if QMessageBox.question(self, "Delete", "Delete selected expense?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.delete_expense(exp_id)
            self.reload()


# ---------------- Whole-period lists ---------------- #
class IncomesListDialog(QDialog):
    """List of incomes in the period with Edit/Delete."""
    def __init__(self, db, start: date, end: date, parent=None):
        super().__init__(parent)
        self.db = db
        self.start = start
        self.end = end
        self.setWindowTitle("Incomes in Period")

        outer = QVBoxLayout(self)

        self.lbl_info = QLabel("")
        outer.addWidget(self.lbl_info)

        # Table: Date, Amount, Source, (hidden ID)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Date", "Amount", "Source", "ID"])
        self.table.setColumnHidden(3, True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemDoubleClicked.connect(lambda *_: self.edit_selected())
        outer.addWidget(self.table)

        # Buttons
        row = QHBoxLayout()
        self.btn_edit = QPushButton("Edit Selected")
        self.btn_delete = QPushButton("Delete Selected")
        self.btn_close = QPushButton("Close")
        self.btn_edit.clicked.connect(self.edit_selected)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_close.clicked.connect(self.reject)
        row.addWidget(self.btn_edit)
        row.addWidget(self.btn_delete)
        row.addStretch()
        row.addWidget(self.btn_close)
        outer.addLayout(row)

        # Footer total
        self.lbl_total = QLabel("Total: 0.00")
        self.lbl_total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        outer.addWidget(self.lbl_total)

        self.reload()

    def reload(self):
        rows = self.db.incomes_in_range(self.start, self.end)
        self.table.setRowCount(0)
        total = 0.0
        for (inc_id, dstr, amt, src) in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(dstr))
            amt_item = QTableWidgetItem(f"{amt:.2f}")
            amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(r, 1, amt_item)
            self.table.setItem(r, 2, QTableWidgetItem(src))
            self.table.setItem(r, 3, QTableWidgetItem(str(inc_id)))
            total += float(amt or 0)

        self.table.resizeColumnsToContents()
        self.lbl_total.setText(f"Total: {total:,.2f}")
        self.lbl_info.setText(f"Items: {len(rows)}")

    def _selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 3).text())

    def edit_selected(self):
        inc_id = self._selected_id()
        if inc_id is None:
            return
        r = self.table.currentRow()
        cur_date = date.fromisoformat(self.table.item(r, 0).text())
        cur_amount = float(self.table.item(r, 1).text())
        cur_source = self.table.item(r, 2).text() or ""

        dlg = EditIncomeDialog(cur_date, cur_amount, cur_source, self)
        res = dlg.get()
        if res:
            d, amount, source = res
            self.db.update_income(inc_id, amount, source, d)
            self.reload()

    def delete_selected(self):
        inc_id = self._selected_id()
        if inc_id is None:
            return
        from PySide6.QtWidgets import QMessageBox
        if QMessageBox.question(self, "Delete", "Delete selected income?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.db.delete_income(inc_id)
            self.reload()


class ExpensesListDialog(QDialog):
    """Read-only list of ALL expenses for the given period."""
    def __init__(self, rows: list[tuple[int, str, float, str, str]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Expenses in Period")
        layout = QVBoxLayout(self)

        total = sum(float(r[2] or 0) for r in rows)
        layout.addWidget(QLabel(f"Items: {len(rows)} — Total: {total:,.2f}"))

        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["Date", "Amount", "Category", "Note"]) 
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(table)

        for (_id, dstr, amt, cat, note) in rows:
            r = table.rowCount()
            table.insertRow(r)
            table.setItem(r, 0, QTableWidgetItem(dstr))
            amt_item = QTableWidgetItem(f"{amt:.2f}")
            amt_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(r, 1, amt_item)
            table.setItem(r, 2, QTableWidgetItem(cat))
            table.setItem(r, 3, QTableWidgetItem(note))

        table.resizeColumnsToContents()

        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(self.reject)
        btns.accepted.connect(self.accept)
        layout.addWidget(btns)

class EditIncomeDialog(QDialog):
    def __init__(self, init_date: date, init_amount: float, init_source: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Income")
        lay = QFormLayout(self)

        self.date = QDateEdit(calendarPopup=True)
        self.date.setDisplayFormat("yyyy-MM-dd")
        self.date.setDate(QDate(init_date.year, init_date.month, init_date.day))

        self.amount = QLineEdit(str(init_amount))
        self.source = QLineEdit(init_source)

        lay.addRow("Date", self.date)
        lay.addRow("Amount", self.amount)
        lay.addRow("Source", self.source)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addRow(btns)

    def get(self):
        if self.exec() == QDialog.Accepted:
            try:
                amt = float(self.amount.text())
            except ValueError:
                QMessageBox.warning(self, "Invalid", "Amount must be a number")
                return None
            return (self.date.date().toPython(), amt, self.source.text().strip())
        return None

class ChartDialog(QDialog):
    """Simple Matplotlib dialog for pie/bar charts."""
    def __init__(self, title: str, labels: list[str], values: list[float], chart: str = "pie", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        layout = QVBoxLayout(self)
        self.fig = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.ax = self.fig.add_subplot(111)
        self._plot(chart, labels, values)

    def _plot(self, chart: str, labels: list[str], values: list[float]):
        self.ax.clear()
        if not values or sum(values) == 0:
            self.ax.text(0.5, 0.5, "No data in range", ha="center", va="center")
        elif chart == "pie":
            self.ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
            self.ax.axis("equal")
        else:  # bar
            bars = self.ax.bar(labels, values)
            self.ax.set_ylabel("Amount")
            self.ax.set_xticklabels(labels, rotation=45, ha="right")
            # optional value labels on top of bars
            for b in bars:
                self.ax.text(b.get_x() + b.get_width()/2, b.get_height(), f"{b.get_height():,.0f}",
                             ha="center", va="bottom")
        self.fig.tight_layout()
        self.canvas.draw()

class DailyExpensesChartDialog(QDialog):
    """Stacked bar char: daily expenses per categroy in the selected period."""
    def __init__(self, dates: list[str], series: dict[str, list[float]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Daily Expenses by Category")
        layout = QVBoxLayout(self)

        self.fig = Figure(figsize=(7,4))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        ax = self.fig.add_subplot(111)

        if not dates or not series:
            ax.text(0.5, 0.5, "No data in range", ha="center", va="center")
        else:
            x = list(range(len(dates)))
            bottoms = [0.0] * len(dates)
            # Plot each category stacked
            for cat, vals in series.items():
                ax.bar(x, vals, bottom=bottoms, label=cat)
                bottoms = [b + v for b, v in zip(bottoms, vals)]
            
            ax.set_xticks(x)
            ax.set_xticklabels(dates, rotation=45, ha="right")
            ax.set_ylabel("Amount")
            ax.legend(loc="upper right", fontsize=8)
        
        self.fig.tight_layout()
        self.canvas.draw()
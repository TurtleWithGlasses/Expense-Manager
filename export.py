"""
Data export functionality for Expense Manager
"""
import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any
import pandas as pd
from PySide6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PySide6.QtCore import QThread, pyqtSignal

class ExportWorker(QThread):
    """Worker thread for data export to prevent UI freezing"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, db, start_date: date, end_date: date, export_type: str, file_path: str):
        super().__init__()
        self.db = db
        self.start_date = start_date
        self.end_date = end_date
        self.export_type = export_type
        self.file_path = file_path
    
    def run(self):
        try:
            if self.export_type == "csv":
                self._export_csv()
            elif self.export_type == "excel":
                self._export_excel()
            elif self.export_type == "json":
                self._export_json()
            else:
                raise ValueError(f"Unsupported export type: {self.export_type}")
            
            self.finished.emit(True, f"Data exported successfully to {self.file_path}")
        except Exception as e:
            self.finished.emit(False, f"Export failed: {str(e)}")
    
    def _export_csv(self):
        """Export data to CSV format"""
        with open(self.file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Export expenses
            writer.writerow(["Type", "Date", "Category", "Amount", "Note"])
            expenses = self.db.expenses_in_range(self.start_date, self.end_date)
            for exp_id, exp_date, amount, category, note in expenses:
                writer.writerow(["Expense", exp_date, category, amount, note])
            
            # Export incomes
            incomes = self.db.incomes_in_range(self.start_date, self.end_date)
            for inc_id, inc_date, amount, source in incomes:
                writer.writerow(["Income", inc_date, "N/A", amount, source])
    
    def _export_excel(self):
        """Export data to Excel format with multiple sheets"""
        with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
            # Expenses sheet
            expenses = self.db.expenses_in_range(self.start_date, self.end_date)
            exp_df = pd.DataFrame(expenses, columns=['ID', 'Date', 'Amount', 'Category', 'Note'])
            exp_df = exp_df.drop('ID', axis=1)  # Remove ID column for cleaner export
            exp_df.to_excel(writer, sheet_name='Expenses', index=False)
            
            # Incomes sheet
            incomes = self.db.incomes_in_range(self.start_date, self.end_date)
            inc_df = pd.DataFrame(incomes, columns=['ID', 'Date', 'Amount', 'Source'])
            inc_df = inc_df.drop('ID', axis=1)  # Remove ID column for cleaner export
            inc_df.to_excel(writer, sheet_name='Incomes', index=False)
            
            # Summary sheet
            summary_data = self._create_summary_data()
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    def _export_json(self):
        """Export data to JSON format"""
        data = {
            "export_info": {
                "start_date": self.start_date.isoformat(),
                "end_date": self.end_date.isoformat(),
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            },
            "expenses": [],
            "incomes": [],
            "categories": [],
            "summary": {}
        }
        
        # Export expenses
        expenses = self.db.expenses_in_range(self.start_date, self.end_date)
        for exp_id, exp_date, amount, category, note in expenses:
            data["expenses"].append({
                "id": exp_id,
                "date": exp_date,
                "amount": amount,
                "category": category,
                "note": note
            })
        
        # Export incomes
        incomes = self.db.incomes_in_range(self.start_date, self.end_date)
        for inc_id, inc_date, amount, source in incomes:
            data["incomes"].append({
                "id": inc_id,
                "date": inc_date,
                "amount": amount,
                "source": source
            })
        
        # Export categories
        categories = self.db.all_categories()
        for cat_id, cat_name in categories:
            data["categories"].append({
                "id": cat_id,
                "name": cat_name
            })
        
        # Add summary
        data["summary"] = self._create_summary_data()
        
        with open(self.file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
    
    def _create_summary_data(self) -> List[Dict[str, Any]]:
        """Create summary data for export"""
        total_income = self.db.total_incomes(self.start_date, self.end_date)
        total_expenses = self.db.total_expenses(self.start_date, self.end_date)
        balance = total_income - total_expenses
        
        # Category breakdown
        category_totals = self.db.sum_by_category(self.start_date, self.end_date)
        
        summary = [
            {"Metric": "Total Income", "Value": total_income},
            {"Metric": "Total Expenses", "Value": total_expenses},
            {"Metric": "Balance", "Value": balance},
            {"Metric": "Period", "Value": f"{self.start_date} to {self.end_date}"}
        ]
        
        # Add category breakdown
        for category, amount in category_totals:
            if amount > 0:
                summary.append({"Metric": f"Category: {category}", "Value": amount})
        
        return summary

class ExportManager:
    """Manager class for handling data exports"""
    
    def __init__(self, parent=None):
        self.parent = parent
    
    def export_data(self, db, start_date: date, end_date: date):
        """Show export dialog and handle data export"""
        # Show file dialog
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.parent,
            "Export Data",
            f"expense_data_{start_date}_{end_date}",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        # Determine export type
        if selected_filter.startswith("CSV"):
            export_type = "csv"
            if not file_path.endswith('.csv'):
                file_path += '.csv'
        elif selected_filter.startswith("Excel"):
            export_type = "excel"
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
        elif selected_filter.startswith("JSON"):
            export_type = "json"
            if not file_path.endswith('.json'):
                file_path += '.json'
        else:
            QMessageBox.warning(self.parent, "Error", "Unsupported file format")
            return
        
        # Create progress dialog
        progress = QProgressDialog("Exporting data...", "Cancel", 0, 0, self.parent)
        progress.setWindowModality(2)  # Qt.WindowModal
        progress.show()
        
        # Create and start worker thread
        self.worker = ExportWorker(db, start_date, end_date, export_type, file_path)
        self.worker.finished.connect(lambda success, message: self._export_finished(success, message, progress))
        self.worker.start()
    
    def _export_finished(self, success: bool, message: str, progress: QProgressDialog):
        """Handle export completion"""
        progress.close()
        if success:
            QMessageBox.information(self.parent, "Export Complete", message)
        else:
            QMessageBox.warning(self.parent, "Export Failed", message)

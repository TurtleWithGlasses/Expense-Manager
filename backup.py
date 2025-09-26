"""
Database backup and restore functionality for Expense Manager
"""
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PySide6.QtCore import QThread, Signal

class BackupWorker(QThread):
    """Worker thread for backup operations"""
    progress = Signal(int)
    finished = Signal(bool, str)
    
    def __init__(self, source_db_path: str, backup_path: str, operation: str):
        super().__init__()
        self.source_db_path = source_db_path
        self.backup_path = backup_path
        self.operation = operation  # 'backup' or 'restore'
    
    def run(self):
        try:
            if self.operation == 'backup':
                self._backup_database()
            elif self.operation == 'restore':
                self._restore_database()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
            
            self.finished.emit(True, f"{self.operation.capitalize()} completed successfully")
        except Exception as e:
            self.finished.emit(False, f"{self.operation.capitalize()} failed: {str(e)}")
    
    def _backup_database(self):
        """Create a backup of the database"""
        # Create backup directory if it doesn't exist
        backup_dir = Path(self.backup_path).parent
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy the database file
        shutil.copy2(self.source_db_path, self.backup_path)
        
        # Verify backup by checking if we can open it
        conn = sqlite3.connect(self.backup_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        if not tables:
            raise Exception("Backup verification failed - no tables found")
    
    def _restore_database(self):
        """Restore database from backup"""
        if not os.path.exists(self.backup_path):
            raise Exception("Backup file not found")
        
        # Create a backup of current database before restoring
        current_backup = f"{self.source_db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if os.path.exists(self.source_db_path):
            shutil.copy2(self.source_db_path, current_backup)
        
        # Restore from backup
        shutil.copy2(self.backup_path, self.source_db_path)
        
        # Verify restore by checking if we can open the database
        conn = sqlite3.connect(self.source_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        if not tables:
            raise Exception("Restore verification failed - no tables found")

class BackupManager:
    """Manager class for handling database backups"""
    
    def __init__(self, parent=None):
        self.parent = parent
    
    def create_backup(self, db_path: str):
        """Create a new backup of the database"""
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"expense_manager_backup_{timestamp}.db"
        
        # Show save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Create Database Backup",
            backup_filename,
            "SQLite Database (*.db);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Create progress dialog
        progress = QProgressDialog("Creating backup...", "Cancel", 0, 0, self.parent)
        progress.setWindowModality(2)  # Qt.WindowModal
        progress.show()
        
        # Create and start worker thread
        self.worker = BackupWorker(db_path, file_path, 'backup')
        self.worker.finished.connect(lambda success, message: self._operation_finished(success, message, progress))
        self.worker.start()
    
    def restore_backup(self, db_path: str):
        """Restore database from backup"""
        # Show open dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Restore Database from Backup",
            "",
            "SQLite Database (*.db);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Confirm restore
        if QMessageBox.question(
            self.parent, 
            "Confirm Restore", 
            f"Are you sure you want to restore from backup?\n\nThis will replace your current database with the backup file.\n\nBackup file: {file_path}",
            QMessageBox.Yes | QMessageBox.No
        ) != QMessageBox.Yes:
            return
        
        # Create progress dialog
        progress = QProgressDialog("Restoring backup...", "Cancel", 0, 0, self.parent)
        progress.setWindowModality(2)  # Qt.WindowModal
        progress.show()
        
        # Create and start worker thread
        self.worker = BackupWorker(db_path, file_path, 'restore')
        self.worker.finished.connect(lambda success, message: self._operation_finished(success, message, progress))
        self.worker.start()
    
    def _operation_finished(self, success: bool, message: str, progress: QProgressDialog):
        """Handle backup/restore completion"""
        progress.close()
        if success:
            QMessageBox.information(self.parent, "Success", message)
        else:
            QMessageBox.warning(self.parent, "Error", message)
    
    def list_backups(self, backup_dir: str = None) -> list:
        """List available backup files"""
        if backup_dir is None:
            backup_dir = os.path.join(os.path.expanduser("~"), "Documents", "ExpenseManager", "backups")
        
        if not os.path.exists(backup_dir):
            return []
        
        backup_files = []
        for file in os.listdir(backup_dir):
            if file.endswith('.db') and 'backup' in file.lower():
                file_path = os.path.join(backup_dir, file)
                stat = os.stat(file_path)
                backup_files.append({
                    'filename': file,
                    'path': file_path,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
        
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x['modified'], reverse=True)
        return backup_files

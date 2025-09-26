"""
Settings dialog for Expense Manager
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,
    QFormLayout, QLineEdit, QComboBox, QCheckBox, QFileDialog, QMessageBox,
    QDialogButtonBox, QGroupBox, QSpinBox, QDoubleSpinBox, QWidget
)
from PySide6.QtCore import Qt
from config import config

class SettingsDialog(QDialog):
    """Settings dialog for configuring the application"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # General tab
        self.general_tab = self.create_general_tab()
        self.tabs.addTab(self.general_tab, "General")
        
        # Database tab
        self.database_tab = self.create_database_tab()
        self.tabs.addTab(self.database_tab, "Database")
        
        # Appearance tab
        self.appearance_tab = self.create_appearance_tab()
        self.tabs.addTab(self.appearance_tab, "Appearance")
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults)
        layout.addWidget(buttons)
    
    def create_general_tab(self):
        """Create general settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Currency settings
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY"])
        layout.addRow("Currency:", self.currency_combo)
        
        # Date format
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(["yyyy-MM-dd", "MM/dd/yyyy", "dd/MM/yyyy", "dd-MM-yyyy"])
        layout.addRow("Date Format:", self.date_format_combo)
        
        # Decimal places
        self.decimal_spin = QSpinBox()
        self.decimal_spin.setRange(0, 4)
        self.decimal_spin.setValue(2)
        layout.addRow("Decimal Places:", self.decimal_spin)
        
        # Auto-update settings
        self.auto_update_check = QCheckBox("Check for updates automatically")
        layout.addRow(self.auto_update_check)
        
        # Update URL
        self.update_url_edit = QLineEdit()
        layout.addRow("Update URL:", self.update_url_edit)
        
        return widget
    
    def create_database_tab(self):
        """Create database settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Database path group
        db_group = QGroupBox("Database Location")
        db_layout = QFormLayout(db_group)
        
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setReadOnly(True)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_database)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.db_path_edit)
        path_layout.addWidget(self.browse_btn)
        db_layout.addRow("Database Path:", path_layout)
        
        layout.addWidget(db_group)
        
        # Database info
        info_group = QGroupBox("Database Information")
        info_layout = QVBoxLayout(info_group)
        
        self.db_info_label = QLabel("Database information will be shown here")
        self.db_info_label.setWordWrap(True)
        info_layout.addWidget(self.db_info_label)
        
        self.refresh_info_btn = QPushButton("Refresh Info")
        self.refresh_info_btn.clicked.connect(self.refresh_db_info)
        info_layout.addWidget(self.refresh_info_btn)
        
        layout.addWidget(info_group)
        layout.addStretch()
        
        return widget
    
    def create_appearance_tab(self):
        """Create appearance settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        layout.addRow("Theme:", self.theme_combo)
        
        # Window size
        size_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(400, 2000)
        self.width_spin.setValue(720)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(300, 1500)
        self.height_spin.setValue(900)
        
        size_layout.addWidget(QLabel("Width:"))
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("Height:"))
        size_layout.addWidget(self.height_spin)
        layout.addRow("Default Window Size:", size_layout)
        
        # Font settings
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(10)
        layout.addRow("Font Size:", self.font_size_spin)
        
        return widget
    
    def load_settings(self):
        """Load current settings into the dialog"""
        self.currency_combo.setCurrentText(config.get("currency", "USD"))
        self.date_format_combo.setCurrentText(config.get("date_format", "yyyy-MM-dd"))
        self.decimal_spin.setValue(config.get("decimal_places", 2))
        self.auto_update_check.setChecked(config.get("auto_update_check", True))
        self.update_url_edit.setText(config.get("update_url", "http://127.0.0.1:9000/latest.json"))
        
        self.db_path_edit.setText(config.get("database_path", ""))
        
        self.theme_combo.setCurrentText(config.get("theme", "Light"))
        self.width_spin.setValue(config.get("window_width", 720))
        self.height_spin.setValue(config.get("window_height", 900))
        self.font_size_spin.setValue(config.get("font_size", 10))
        
        self.refresh_db_info()
    
    def save_settings(self):
        """Save settings to configuration"""
        config.set("currency", self.currency_combo.currentText())
        config.set("date_format", self.date_format_combo.currentText())
        config.set("decimal_places", self.decimal_spin.value())
        config.set("auto_update_check", self.auto_update_check.isChecked())
        config.set("update_url", self.update_url_edit.text())
        
        config.set("database_path", self.db_path_edit.text())
        
        config.set("theme", self.theme_combo.currentText())
        config.set("window_width", self.width_spin.value())
        config.set("window_height", self.height_spin.value())
        config.set("font_size", self.font_size_spin.value())
        
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        self.accept()
    
    def restore_defaults(self):
        """Restore default settings"""
        if QMessageBox.question(self, "Restore Defaults", 
                              "Are you sure you want to restore all settings to defaults?",
                              QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            config.reset_to_defaults()
            self.load_settings()
    
    def browse_database(self):
        """Browse for database file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Database File", "", "SQLite Database (*.db);;All Files (*)"
        )
        if file_path:
            self.db_path_edit.setText(file_path)
    
    def refresh_db_info(self):
        """Refresh database information"""
        db_path = self.db_path_edit.text()
        if not db_path:
            self.db_info_label.setText("No database path specified")
            return
        
        try:
            import os
            from pathlib import Path
            
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                size_mb = size / (1024 * 1024)
                modified = os.path.getmtime(db_path)
                from datetime import datetime
                modified_str = datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M:%S")
                
                info = f"Database exists\nSize: {size_mb:.2f} MB\nLast modified: {modified_str}"
            else:
                info = "Database file does not exist"
        except Exception as e:
            info = f"Error reading database info: {str(e)}"
        
        self.db_info_label.setText(info)

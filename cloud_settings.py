"""
Cloud Database Settings Dialog for Expense Manager
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,
    QFormLayout, QLineEdit, QComboBox, QMessageBox,
    QDialogButtonBox, QGroupBox, QSpinBox, QWidget, QTextEdit
)
from config import config

class CloudDatabaseSettingsDialog(QDialog):
    """Settings dialog for configuring cloud database connection"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cloud Database Settings")
        self.setMinimumSize(600, 500)
        
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self._create_database_tab()
        self._create_cloud_tab()
        self._create_test_tab()
        
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        self._load_settings()
    
    def _create_database_tab(self):
        """Create database type selection tab"""
        db_tab = QWidget()
        layout = QFormLayout(db_tab)
        
        self.db_type_combo = QComboBox()
        self.db_type_combo.addItems(["SQLite (Local)", "PostgreSQL (Cloud)"])
        self.db_type_combo.currentTextChanged.connect(self._on_db_type_changed)
        
        layout.addRow("Database Type:", self.db_type_combo)
        
        # Local database path
        self.db_path_input = QLineEdit()
        self.db_path_input.setReadOnly(True)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_db_path)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.db_path_input)
        path_layout.addWidget(browse_btn)
        layout.addRow("Local Database Path:", path_layout)
        
        self.tabs.addTab(db_tab, "Database Type")
    
    def _create_cloud_tab(self):
        """Create cloud database configuration tab"""
        cloud_tab = QWidget()
        layout = QFormLayout(cloud_tab)
        
        # Connection settings
        connection_group = QGroupBox("Connection Settings")
        connection_layout = QFormLayout(connection_group)
        
        self.host_input = QLineEdit()
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(5432)
        
        self.database_input = QLineEdit()
        self.user_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        connection_layout.addRow("Host:", self.host_input)
        connection_layout.addRow("Port:", self.port_input)
        connection_layout.addRow("Database:", self.database_input)
        connection_layout.addRow("Username:", self.user_input)
        connection_layout.addRow("Password:", self.password_input)
        
        layout.addWidget(connection_group)
        
        # Instructions
        instructions = QTextEdit()
        instructions.setMaximumHeight(150)
        instructions.setReadOnly(True)
        instructions.setHtml("""
        <h3>Cloud Database Setup Instructions:</h3>
        <p><b>Option 1: Supabase (Recommended)</b></p>
        <ol>
        <li>Go to <a href="https://supabase.com">supabase.com</a></li>
        <li>Create a free account and new project</li>
        <li>Go to Settings → Database</li>
        <li>Copy the connection details</li>
        </ol>
        
        <p><b>Option 2: PythonAnywhere</b></p>
        <ol>
        <li>Upgrade to paid account</li>
        <li>Create a MySQL database</li>
        <li>Use MySQL connection details</li>
        </ol>
        """)
        
        layout.addWidget(instructions)
        
        self.tabs.addTab(cloud_tab, "Cloud Configuration")
    
    def _create_test_tab(self):
        """Create database connection test tab"""
        test_tab = QWidget()
        layout = QVBoxLayout(test_tab)
        
        # Test connection button
        test_btn = QPushButton("Test Database Connection")
        test_btn.clicked.connect(self._test_connection)
        layout.addWidget(test_btn)
        
        # Test results
        self.test_results = QTextEdit()
        self.test_results.setReadOnly(True)
        self.test_results.setMaximumHeight(200)
        layout.addWidget(QLabel("Test Results:"))
        layout.addWidget(self.test_results)
        
        # Migration info
        migration_info = QTextEdit()
        migration_info.setReadOnly(True)
        migration_info.setMaximumHeight(150)
        migration_info.setHtml("""
        <h3>Database Migration:</h3>
        <p>When switching to cloud database:</p>
        <ul>
        <li>Your local data will be migrated automatically</li>
        <li>All categories, expenses, incomes, and budgets will be transferred</li>
        <li>Your local database will remain as backup</li>
        <li>You can switch back to local database anytime</li>
        </ul>
        """)
        
        layout.addWidget(migration_info)
        
        self.tabs.addTab(test_tab, "Test & Migration")
    
    def _on_db_type_changed(self, text):
        """Handle database type change"""
        is_cloud = "PostgreSQL" in text
        self.tabs.setTabEnabled(1, is_cloud)  # Enable/disable cloud tab
    
    def _browse_db_path(self):
        """Browse for local database file"""
        from PySide6.QtWidgets import QFileDialog
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Select Database File", "", "SQLite Database (*.db)"
        )
        if file_name:
            self.db_path_input.setText(file_name)
    
    def _load_settings(self):
        """Load current settings"""
        db_type = config.get("database_type", "sqlite")
        if db_type == "postgresql":
            self.db_type_combo.setCurrentText("PostgreSQL (Cloud)")
        else:
            self.db_type_combo.setCurrentText("SQLite (Local)")
        
        self.db_path_input.setText(config.get("database_path", ""))
        
        cloud_config = config.get("cloud_database", {})
        self.host_input.setText(cloud_config.get("host", ""))
        self.port_input.setValue(cloud_config.get("port", 5432))
        self.database_input.setText(cloud_config.get("database", ""))
        self.user_input.setText(cloud_config.get("user", ""))
        self.password_input.setText(cloud_config.get("password", ""))
    
    def _test_connection(self):
        """Test database connection"""
        try:
            from cloud_db import CloudDatabase
            
            db_type = "postgresql" if "PostgreSQL" in self.db_type_combo.currentText() else "sqlite"
            
            if db_type == "postgresql":
                # Test PostgreSQL connection
                host = self.host_input.text().strip()
                port = self.port_input.value()
                database = self.database_input.text().strip()
                user = self.user_input.text().strip()
                password = self.password_input.text().strip()
                
                if not all([host, database, user, password]):
                    self.test_results.setText("❌ Please fill in all connection details")
                    return
                
                with CloudDatabase(
                    db_type="postgresql",
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password
                ) as db:
                    self.test_results.setText("✅ PostgreSQL connection successful!\n\nDatabase is ready to use.")
                    
            else:
                # Test SQLite connection
                db_path = self.db_path_input.text().strip()
                if not db_path:
                    self.test_results.setText("❌ Please specify a database path")
                    return
                
                with CloudDatabase(db_type="sqlite") as _:
                    self.test_results.setText("✅ SQLite connection successful!\n\nDatabase is ready to use.")
                    
        except Exception as e:
            self.test_results.setText(f"❌ Connection failed:\n\n{str(e)}")
    
    def save_settings(self):
        """Save settings to configuration"""
        try:
            # Determine database type
            db_type = "postgresql" if "PostgreSQL" in self.db_type_combo.currentText() else "sqlite"
            
            # Update configuration
            config.set("database_type", db_type)
            config.set("database_path", self.db_path_input.text())
            
            if db_type == "postgresql":
                cloud_config = {
                    "host": self.host_input.text().strip(),
                    "port": self.port_input.value(),
                    "database": self.database_input.text().strip(),
                    "user": self.user_input.text().strip(),
                    "password": self.password_input.text().strip()
                }
                config.set("cloud_database", cloud_config)
            
            QMessageBox.information(self, "Settings Saved", 
                                  "Database settings have been saved.\n\n"
                                  "Restart the application to apply changes.")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save settings: {e}")

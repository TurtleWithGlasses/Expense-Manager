"""
Configuration settings for Expense Manager
"""
import os
import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration manager for Expense Manager"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".expense_manager"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        
        # Default configuration
        self.defaults = {
            "database_path": str(Path.home() / "Documents" / "ExpenseManager" / "expenses.db"),
            "auto_update_check": True,
            "update_url": "http://127.0.0.1:9000/latest.json",
            "window_width": 720,
            "window_height": 900,
            "theme": "light",
            "currency": "USD",
            "date_format": "yyyy-MM-dd",
            "decimal_places": 2,
            "database_type": "sqlite",  # "sqlite" or "postgresql"
            "cloud_database": {
                "host": "",
                "port": 5432,
                "database": "",
                "user": "",
                "password": ""
            }
        }
        
        self.settings = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**self.defaults, **config}
            except (json.JSONDecodeError, IOError):
                pass
        return self.defaults.copy()
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Failed to save config: {e}")
    
    def get(self, key: str, default=None):
        """Get a configuration value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        self.settings[key] = value
        self.save_config()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.defaults.copy()
        self.save_config()

# Global config instance
config = Config()

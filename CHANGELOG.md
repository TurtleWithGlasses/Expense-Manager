# Changelog

All notable changes to Expense Manager will be documented in this file.

## [1.1.0] - 2024-01-XX

### Added
- **Comprehensive README.md** with detailed installation and usage instructions
- **Configuration Management** - Configurable database path and application settings
- **Data Export Functionality** - Export data to CSV, Excel, and JSON formats
- **Budget Tracking** - Set budgets for categories with progress monitoring and alerts
- **Database Backup & Restore** - Create and restore database backups
- **Settings Dialog** - Comprehensive settings management for all preferences
- **Budget Status Indicator** - Real-time budget status display on dashboard
- **Unit Tests** - Basic test suite for core functionality
- **Installation Script** - Automated installation with dependency management
- **Build Script** - Automated executable building and packaging

### Changed
- **Database Path** - Now uses configurable path instead of hardcoded location
- **UI Enhancements** - Added budget status display and improved menu structure
- **Error Handling** - Better error handling and user feedback

### Fixed
- **Database Location** - Fixed hardcoded database path issue
- **Import Issues** - Resolved missing imports and dependencies

### Technical Improvements
- **Modular Architecture** - Separated concerns into dedicated modules
- **Configuration System** - Centralized configuration management
- **Thread Safety** - Added worker threads for long-running operations
- **Code Quality** - Improved code organization and documentation

## [1.0.0] - 2024-01-XX

### Initial Release
- Basic expense and income tracking
- Category management
- Data visualization (charts)
- SQLite database storage
- Auto-updater functionality
- PyInstaller build configuration

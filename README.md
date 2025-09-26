# 💰 Expense Manager

A modern, cross-platform desktop application for personal expense and income tracking built with PySide6 and SQLite.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 📊 **Dashboard & Analytics**
- Interactive dashboard with real-time statistics
- Visual charts (pie charts, bar charts, daily trends)
- Period-based filtering (day, week, month, custom range)
- Category-wise expense breakdown
- Income vs Expense comparison

### 💳 **Transaction Management**
- Add, edit, and delete expenses and incomes
- Categorized expense tracking
- Income source tracking
- Transaction notes and descriptions
- Date-based transaction history

### 📁 **Category Management**
- Create custom expense categories
- Edit and delete categories
- Automatic category creation for new expenses
- Category-wise expense analysis

### 📈 **Reporting & Visualization**
- Pie charts for expense distribution
- Bar charts for category comparisons
- Daily expense trends with stacked bars
- Exportable reports and data

### 🔄 **Additional Features**
- Auto-updater with version checking
- Cross-platform compatibility (Windows, macOS, Linux)
- SQLite database for reliable data storage
- Modern, responsive UI design

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### From Source
1. Clone the repository:
```bash
git clone https://github.com/TurtleWithGlasses/Expense-Manager.git
cd Expense-Manager
```

2. Create a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

### Pre-built Executable
Download the latest release from the [Releases](https://github.com/TurtleWithGlasses/Expense-Manager/releases) page and run the installer.

## 📖 Usage

### Getting Started
1. **Launch the application** - The dashboard will open with current month's data
2. **Add your first income** - Click the "Income" button to add salary or other income
3. **Create expense categories** - Use "Add Category" to create categories like "Food", "Transport", etc.
4. **Track expenses** - Click "Expense" to add your daily expenses

### Dashboard Overview
- **Period Selection**: Use Month/Week/Day buttons or custom date range
- **Statistics Boxes**: Click on Income/Expense totals to view detailed lists
- **Category Cards**: Click any category to see detailed expenses
- **Charts**: Use Pie/Bars/Daily buttons to visualize your spending patterns

### Managing Data
- **Edit Transactions**: Double-click any transaction in the detailed views
- **Delete Transactions**: Select and use the delete button
- **Category Management**: Add, edit, or delete categories as needed

## 🛠️ Development

### Project Structure
```
Expense-Manager/
├── main.py              # Main application window
├── db.py                # Database operations
├── dialogs.py           # Dialog windows
├── widgets.py           # Custom UI components
├── updater.py           # Auto-update functionality
├── version.py           # Version information
├── requirements.txt     # Python dependencies
├── assets/              # Icons and resources
├── build/               # PyInstaller build output
└── dist/                # Distribution files
```

### Building from Source
1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
pyinstaller ExpenseManager.spec
```

3. Find the executable in the `dist/` folder

### Database Schema
- **categories**: Expense categories (id, name, created_at)
- **expenses**: Individual expenses (id, category_id, amount, note, date)
- **incomes**: Income records (id, amount, source, date)

## 🔧 Configuration

### Database Location
The application uses SQLite and stores data in:
- **Default**: `H:\My Drive\databases\expenses.db`
- **Custom**: Modify `DB_FILE` in `db.py`

### Auto-Updates
Update checking is configured in `updater.py`:
- **Update URL**: `http://127.0.0.1:9000/latest.json`
- **Check on startup**: Automatic (silent)
- **Manual check**: Help menu

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python
- Charts powered by [Matplotlib](https://matplotlib.org/)
- Database: [SQLite](https://www.sqlite.org/)
- Icons: Custom design

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/TurtleWithGlasses/Expense-Manager/issues) page
2. Create a new issue with detailed description
3. Include your operating system and Python version

---

**Happy Budgeting! 💰**

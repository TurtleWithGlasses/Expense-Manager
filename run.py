#!/usr/bin/env python3
"""
Launcher script for Expense Manager
"""
import sys
import os
from pathlib import Path

def main():
    """Launch Expense Manager"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Import and run the main application
    try:
        from main import main as run_app
        run_app()
    except ImportError as e:
        print(f"Error importing application: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

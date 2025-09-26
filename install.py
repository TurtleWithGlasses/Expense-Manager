#!/usr/bin/env python3
"""
Installation script for Expense Manager
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)"""
    if platform.system() != "Windows":
        return
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Expense Manager.lnk")
        target = os.path.join(os.getcwd(), "main.py")
        wDir = os.getcwd()
        icon = os.path.join(os.getcwd(), "money_icon.png")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()
        
        print("✓ Desktop shortcut created")
    except ImportError:
        print("Note: Desktop shortcut creation requires pywin32 package")
    except Exception as e:
        print(f"Note: Could not create desktop shortcut: {e}")

def create_start_menu_shortcut():
    """Create start menu shortcut (Windows only)"""
    if platform.system() != "Windows":
        return
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        start_menu = winshell.start_menu()
        programs = os.path.join(start_menu, "Programs")
        expense_manager_dir = os.path.join(programs, "Expense Manager")
        os.makedirs(expense_manager_dir, exist_ok=True)
        
        path = os.path.join(expense_manager_dir, "Expense Manager.lnk")
        target = os.path.join(os.getcwd(), "main.py")
        wDir = os.getcwd()
        icon = os.path.join(os.getcwd(), "money_icon.png")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()
        
        print("✓ Start menu shortcut created")
    except ImportError:
        print("Note: Start menu shortcut creation requires pywin32 package")
    except Exception as e:
        print(f"Note: Could not create start menu shortcut: {e}")

def main():
    """Main installation function"""
    print("Expense Manager Installation")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Create shortcuts (Windows only)
    if platform.system() == "Windows":
        create_desktop_shortcut()
        create_start_menu_shortcut()
    
    print("\n✓ Installation completed successfully!")
    print("\nTo run Expense Manager:")
    print("  python main.py")
    print("\nOr double-click the desktop shortcut (Windows)")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)

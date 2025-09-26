#!/usr/bin/env python3
"""
Build script for Expense Manager
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous build...")
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ Removed {dir_name}")
    
    # Clean .pyc files
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pyc"):
                os.remove(os.path.join(root, file))

def build_executable():
    """Build executable using PyInstaller"""
    print("Building executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=ExpenseManager",
        "--icon=money_icon.png",
        "--add-data=money_icon.png;.",
        "main.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✓ Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        return False

def create_installer():
    """Create installer using Inno Setup (Windows only)"""
    if sys.platform != "win32":
        print("Note: Installer creation is only supported on Windows")
        return True
    
    if not os.path.exists("installer/expense_manager.iss"):
        print("Note: Inno Setup script not found, skipping installer creation")
        return True
    
    print("Creating installer...")
    try:
        # Find Inno Setup compiler
        inno_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
            r"C:\Program Files\Inno Setup 5\ISCC.exe"
        ]
        
        inno_exe = None
        for path in inno_paths:
            if os.path.exists(path):
                inno_exe = path
                break
        
        if not inno_exe:
            print("Note: Inno Setup not found, skipping installer creation")
            return True
        
        # Run Inno Setup
        cmd = [inno_exe, "installer/expense_manager.iss"]
        subprocess.check_call(cmd)
        print("✓ Installer created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating installer: {e}")
        return False

def main():
    """Main build function"""
    print("Expense Manager Build Script")
    print("=" * 30)
    
    # Clean previous builds
    clean_build()
    
    # Build executable
    if not build_executable():
        return False
    
    # Create installer
    create_installer()
    
    print("\n✓ Build completed successfully!")
    print(f"Executable location: {os.path.join('dist', 'ExpenseManager.exe')}")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)

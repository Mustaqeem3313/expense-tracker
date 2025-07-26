#!/usr/bin/env python3
"""
Setup verification script for Expense Tracker application
"""

import sys
import os
import sqlite3
from importlib import import_module

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_wtf',
        'wtforms',
        'werkzeug',
        'reportlab',
        'PIL',
        'dateutil'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            import_module(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            missing_packages.append(package)

    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False

    return True

def check_directory_structure():
    """Check if all required directories exist"""
    required_dirs = [
        'app',
        'app/static',
        'app/static/css',
        'app/static/js',
        'app/static/images',
        'app/templates',
        'app/routes'
    ]

    missing_dirs = []

    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/ exists")
        else:
            print(f"❌ {directory}/ is missing")
            missing_dirs.append(directory)

    if missing_dirs:
        print(f"\nMissing directories: {', '.join(missing_dirs)}")
        return False

    return True

def check_database():
    """Check if database can be created"""
    try:
        conn = sqlite3.connect(':memory:')
        conn.execute('CREATE TABLE test (id INTEGER PRIMARY KEY)')
        conn.close()
        print("✅ SQLite database functionality works")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Run all setup checks"""
    print("🔍 Expense Tracker Setup Verification\n")

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Directory Structure", check_directory_structure),
        ("Database", check_database)
    ]

    all_passed = True

    for check_name, check_func in checks:
        print(f"\n--- {check_name} ---")
        if not check_func():
            all_passed = False

    print("\n" + "="*50)

    if all_passed:
        print("🎉 All checks passed! Your setup is ready.")
        print("Run 'python run.py' to start the application.")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()

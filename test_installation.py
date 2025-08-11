#!/usr/bin/env python3
"""
Test script to verify FinGenius installation
This script checks if all required components are properly installed
"""

import sys
import os
import importlib.util
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.12 or higher"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 12):
        print(f"✗ Python version is too old: {version.major}.{version.minor}")
        print("  FinGenius requires Python 3.12 or higher")
        return False
    else:
        print(f"✓ Python version {version.major}.{version.minor} is compatible")
        return True

def check_required_files():
    """Check if required files exist"""
    print("\nChecking required files...")
    required_files = [
        "main.py",
        "requirements.txt",
        "config/config.example.toml",
        "src/__init__.py",
        "src/config.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("✗ Missing required files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("✓ All required files are present")
        return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\nChecking dependencies...")
    required_packages = [
        "streamlit",
        "asyncio",
        "pydantic",
        "aiohttp",
        "openai",
        "fastmcp",
        "pandas",
        "numpy",
        "matplotlib",
        "tomli",
        "mcp",
        "tenacity",
        "loguru",
        "rich"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.util.find_spec(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("✗ Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        return False
    else:
        print("✓ All required packages are installed")
        return True

def check_project_modules():
    """Check if project modules can be imported"""
    print("\nChecking project modules...")
    project_modules = [
        "src.config",
        "src.logger",
        "src.schema",
        "src.agent.base",
        "src.environment.base",
        "src.tool.base"
    ]
    
    failed_imports = []
    for module in project_modules:
        try:
            importlib.import_module(module)
        except ImportError as e:
            failed_imports.append((module, str(e)))
    
    if failed_imports:
        print("✗ Failed to import project modules:")
        for module, error in failed_imports:
            print(f"  - {module}: {error}")
        return False
    else:
        print("✓ All project modules can be imported")
        return True

def check_config_file():
    """Check if config file can be loaded"""
    print("\nChecking configuration...")
    try:
        from src.config import config
        print("✓ Configuration file loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False

def main():
    """Main function to run all checks"""
    print("=== FinGenius Installation Verification ===")
    
    checks = [
        check_python_version,
        check_required_files,
        check_dependencies,
        check_project_modules,
        check_config_file
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"✗ Check failed with exception: {e}")
            results.append(False)
    
    print("\n=== Summary ===")
    if all(results):
        print("✓ All checks passed! FinGenius is properly installed.")
        print("\nNext steps:")
        print("1. Edit config/config.toml to add your API keys")
        print("2. Activate the virtual environment:")
        print("   - Unix/macOS: source .venv/bin/activate")
        print("   - Windows: .venv\\Scripts\\activate")
        print("3. Run the application: python main.py STOCK_CODE")
        return 0
    else:
        print("✗ Some checks failed. Please review the errors above.")
        print("  You may need to reinstall or check your installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
@echo off
REM FinGenius Automatic Installation Script for Windows
REM This script automates the installation process for the FinGenius project on Windows

echo === FinGenius Automatic Installation for Windows ===
echo This script will install the FinGenius project with all its dependencies.
echo.

REM Function to check if a command exists
where /q python >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python is not installed or not in PATH. Please install Python 3.12 or higher.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Found Python version: %PYTHON_VERSION%

REM Check if Python version is 3.12 or higher
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% lss 3 (
    echo ✗ Python version is too old. FinGenius requires Python 3.12 or higher.
    pause
    exit /b 1
)

if %MAJOR% equ 3 (
    if %MINOR% lss 12 (
        echo ✗ Python version is too old. FinGenius requires Python 3.12 or higher.
        pause
        exit /b 1
    )
)

echo ✓ Python version is compatible (3.12+)

echo.
echo Installing uv package manager...
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

REM Check if uv was installed successfully
where /q uv >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Failed to install uv. Please install it manually and run this script again.
    pause
    exit /b 1
)

echo ✓ uv installation completed

echo.
echo Cloning FinGenius repository...
where /q git >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Git is not installed or not in PATH. Please install Git to clone the repository.
    pause
    exit /b 1
)

if exist FinGenius (
    echo ✓ FinGenius directory already exists
    cd FinGenius
) else (
    git clone https://github.com/HuaYaoAI/FinGenius.git
    if %errorlevel% neq 0 (
        echo ✗ Failed to clone repository. Please check your internet connection and try again.
        pause
        exit /b 1
    )
    cd FinGenius
)

echo ✓ Repository cloned/verified

echo.
echo Creating virtual environment...
uv venv --python 3.12
if %errorlevel% neq 0 (
    echo ✗ Failed to create virtual environment. Please check the error message above.
    pause
    exit /b 1
)

echo ✓ Virtual environment created

echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ✗ Failed to activate virtual environment. Please check the error message above.
    pause
    exit /b 1
)

echo ✓ Virtual environment activated

echo.
echo Installing project dependencies...
if not exist requirements.txt (
    echo ✗ requirements.txt not found. Make sure you are in the FinGenius directory.
    pause
    exit /b 1
)

uv pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ✗ Failed to install dependencies. Please check the error message above.
    pause
    exit /b 1
)

echo ✓ Dependencies installed

echo.
echo Creating configuration file...
if not exist config\config.example.toml (
    echo ✗ config/config.example.toml not found.
    pause
    exit /b 1
)

copy config\config.example.toml config\config.toml
if %errorlevel% neq 0 (
    echo ✗ Failed to create configuration file. Please check the error message above.
    pause
    exit /b 1
)

echo ✓ Configuration file created: config/config.toml
echo   Please edit this file to add your API keys and customize settings.

echo.
echo Verifying installation...
if not exist main.py (
    echo ✗ main.py not found. Installation may be incomplete.
    pause
    exit /b 1
)

python -c "import src.config" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Some Python modules could not be imported. There might be an issue with the installation.
) else (
    echo ✓ Python modules imported successfully
)

echo ✓ Installation verification completed

echo.
echo === Installation Completed Successfully ===
echo.
echo Next steps:
echo 1. Edit config/config.toml to add your API keys and customize settings
echo 2. Activate the virtual environment: .venv\Scripts\activate.bat
echo 3. Run the application: python main.py STOCK_CODE
echo.
echo Example: python main.py 000001
echo.
echo For more information, please read the INSTALLATION_GUIDE.md file.
echo.
pause
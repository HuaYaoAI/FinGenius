@echo off
REM FinGenius Enhanced Automatic Installation Script for Windows
REM This script automates the installation process for the FinGenius project on Windows with improved features

REM Set title for the command window
title FinGenius Enhanced Installer

REM Global variables
set LOG_FILE=fingenius_install.log
set CHECKPOINT_FILE=.install_checkpoint
set BACKUP_DIR=.backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set INSTALL_TYPE=full
set INTERACTIVE_MODE=false
set START_TIME=%time%

REM Replace spaces and colons in backup directory name
set BACKUP_DIR=%BACKUP_DIR: =0%
set BACKUP_DIR=%BACKUP_DIR::=%

REM Function to print colored output
:print_info
echo ℹ %~1
call :log_message INFO "%~1"
exit /b

:print_success
echo ✓ %~1
call :log_message INFO "%~1"
exit /b

:print_warning
echo ⚠ %~1
call :log_message WARN "%~1"
exit /b

:print_error
echo ✗ %~1
call :log_message ERROR "%~1"
exit /b

REM Function to log messages with timestamps
:log_message
set LEVEL=%~1
set MESSAGE=%~2
echo [%date% %time%] [%LEVEL%] %MESSAGE% >> "%LOG_FILE%"
exit /b

REM Function to get current timestamp in seconds (approximation)
:get_timestamp
set HOUR=%time:~0,2%
if "%HOUR:~0,1%" == " " set HOUR=0%HOUR:~1,1%
set MIN=%time:~3,2%
if "%MIN:~0,1%" == " " set MIN=0%MIN:~1,1%
set SEC=%time:~6,2%
if "%SEC:~0,1%" == " " set SEC=0%SEC:~1,1%
set TIMESTAMP=%HOUR%%MIN%%SEC%
exit /b

REM Function to create checkpoint
:create_checkpoint
echo %~1 > "%CHECKPOINT_FILE%"
call :log_message INFO "Checkpoint created: %~1"
exit /b

REM Function to restore from checkpoint
:restore_checkpoint
if exist "%CHECKPOINT_FILE%" (
    set /p CHECKPOINT=<"%CHECKPOINT_FILE%"
    call :print_warning "Found previous installation attempt at step: !CHECKPOINT!"
    call :log_message INFO "Found previous installation attempt at step: !CHECKPOINT!"
    exit /b 0
) else (
    exit /b 1
)

REM Function to create backup
:create_backup
if exist FinGenius (
    call :print_info "Creating backup of existing installation..."
    if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
    xcopy FinGenius "%BACKUP_DIR%\FinGenius\" /E /I /H /Y >nul 2>&1
    call :print_success "Backup created in %BACKUP_DIR%"
    call :log_message INFO "Backup created in %BACKUP_DIR%"
)
exit /b

REM Function to rollback installation
:rollback_installation
call :print_warning "Rolling back installation..."
call :log_message INFO "Rolling back installation"

REM Restore from backup if available
if exist "%BACKUP_DIR%\FinGenius" (
    call :print_info "Restoring from backup..."
    rd /s /q FinGenius >nul 2>&1
    xcopy "%BACKUP_DIR%\FinGenius" FinGenius\ /E /I /H /Y >nul 2>&1
    call :print_success "Restored from backup"
    call :log_message INFO "Restored from backup"
) else (
    REM Clean up partial installation
    call :print_info "Cleaning up partial installation..."
    rd /s /q FinGenius .venv >nul 2>&1
    call :print_success "Cleanup completed"
    call :log_message INFO "Cleanup completed"
)
exit /b

REM Function to display usage
:usage
echo Usage: %0 [OPTIONS]
echo Options:
echo   -h, --help          Display this help message
echo   -i, --interactive   Interactive configuration mode
echo   -t, --type TYPE     Installation type (minimal^|full^|development^) [default: full]
echo   -r, --rollback      Rollback previous installation attempt
echo.
echo Examples:
echo   %0                  ^| Standard installation
echo   %0 -i               ^| Interactive installation
echo   %0 -t minimal       ^| Minimal installation
echo   %0 -t development   ^| Development installation
echo   %0 -r               ^| Rollback previous attempt
exit /b

REM Parse command line arguments
:parse_args
:parse_loop
if "%~1" == "" goto parse_end
if "%~1" == "-h" goto show_help
if "%~1" == "--help" goto show_help
if "%~1" == "-i" (
    set INTERACTIVE_MODE=true
    shift
    goto parse_loop
)
if "%~1" == "--interactive" (
    set INTERACTIVE_MODE=true
    shift
    goto parse_loop
)
if "%~1" == "-t" (
    set INSTALL_TYPE=%~2
    if not "!INSTALL_TYPE!" == "minimal" (
        if not "!INSTALL_TYPE!" == "full" (
            if not "!INSTALL_TYPE!" == "development" (
                call :print_error "Invalid installation type. Use minimal, full, or development."
                exit /b 1
            )
        )
    )
    shift
    shift
    goto parse_loop
)
if "%~1" == "--type" (
    set INSTALL_TYPE=%~2
    if not "!INSTALL_TYPE!" == "minimal" (
        if not "!INSTALL_TYPE!" == "full" (
            if not "!INSTALL_TYPE!" == "development" (
                call :print_error "Invalid installation type. Use minimal, full, or development."
                exit /b 1
            )
        )
    )
    shift
    shift
    goto parse_loop
)
if "%~1" == "-r" (
    call :print_info "Rolling back previous installation..."
    call :rollback_installation
    call :print_success "Rollback completed"
    exit /b 0
)
if "%~1" == "--rollback" (
    call :print_info "Rolling back previous installation..."
    call :rollback_installation
    call :print_success "Rollback completed"
    exit /b 0
)
call :print_error "Unknown option: %~1"
call :usage
exit /b 1

:show_help
call :usage
exit /b 0

:parse_end

REM Enable delayed expansion
setlocal enabledelayedexpansion

echo === FinGenius Enhanced Automatic Installation for Windows ===
echo This script will install the FinGenius project with all its dependencies.
echo Installation type: %INSTALL_TYPE%
echo Interactive mode: %INTERACTIVE_MODE%
echo Log file: %LOG_FILE%
echo.

REM Parse command line arguments
call :parse_args %*

REM Check for existing checkpoint
call :restore_checkpoint
if !errorlevel! equ 0 (
    set /p RESUME_CHOICE=Do you want to resume from the previous installation attempt? (y/n): 
    if /i not "!RESUME_CHOICE!" == "y" (
        call :print_info "Starting fresh installation..."
        del "%CHECKPOINT_FILE%" >nul 2>&1
    )
)

REM Create backup of existing installation
call :create_backup

REM Check if Python is installed
call :print_info "Checking Python version..."
call :create_checkpoint "check_python_version"

where /q python >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Python is not installed or not in PATH. Please install Python 3.12 or higher."
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
call :print_info "Found Python version: !PYTHON_VERSION!"

REM Check if Python version is 3.12 or higher
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if !MAJOR! lss 3 (
    call :print_error "Python version is too old. FinGenius requires Python 3.12 or higher."
    pause
    exit /b 1
)

if !MAJOR! equ 3 (
    if !MINOR! lss 12 (
        call :print_error "Python version is too old. FinGenius requires Python 3.12 or higher."
        pause
        exit /b 1
    )
)

call :print_success "Python version is compatible (3.12+)"

echo.

REM Install uv package manager
call :print_info "Installing uv package manager..."
call :create_checkpoint "install_uv"

where /q uv >nul 2>&1
if %errorlevel% neq 0 (
    call :print_info "Downloading and installing uv..."
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    if !errorlevel! neq 0 (
        call :print_error "Failed to install uv. Please install it manually and run this script again."
        pause
        exit /b 1
    )
) else (
    call :print_success "uv is already installed"
)

where /q uv >nul 2>&1
if %errorlevel% neq 0 (
    call :print_warning "uv was installed but is not in PATH. Please restart your terminal or check your PATH environment variable."
)

call :print_success "uv installation completed"

echo.

REM Clone repository
call :print_info "Cloning FinGenius repository..."
call :create_checkpoint "clone_repository"

where /q git >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Git is not installed or not in PATH. Please install Git to clone the repository."
    pause
    exit /b 1
)

if exist FinGenius (
    call :print_success "FinGenius directory already exists"
    cd FinGenius
) else (
    git clone https://github.com/HuaYaoAI/FinGenius.git
    if !errorlevel! neq 0 (
        call :print_error "Failed to clone repository. Please check your internet connection and try again."
        pause
        exit /b 1
    )
    cd FinGenius
)

call :print_success "Repository cloned/verified"

echo.

REM Create virtual environment
call :print_info "Creating virtual environment..."
call :create_checkpoint "create_virtual_environment"

where /q uv >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "uv is not available. Please install uv first."
    pause
    exit /b 1
)

uv venv --python 3.12
if !errorlevel! neq 0 (
    call :print_error "Failed to create virtual environment. Please check the error message above."
    pause
    exit /b 1
)

call :print_success "Virtual environment created"

echo.

REM Activate virtual environment
call :print_info "Activating virtual environment..."
call .venv\Scripts\activate.bat
if !errorlevel! neq 0 (
    call :print_error "Failed to activate virtual environment. Please check the error message above."
    pause
    exit /b 1
)

call :print_success "Virtual environment activated"

echo.

REM Install dependencies
call :print_info "Installing project dependencies..."
call :create_checkpoint "install_dependencies"

if not exist requirements.txt (
    call :print_error "requirements.txt not found. Make sure you are in the FinGenius directory."
    pause
    exit /b 1
)

if "!INSTALL_TYPE!" == "minimal" (
    call :print_info "Installing minimal dependencies..."
    uv pip install -r requirements.txt
    if !errorlevel! neq 0 (
        call :print_error "Failed to install minimal dependencies. Please check the error message above."
        pause
        exit /b 1
    )
    call :print_success "Minimal dependencies installed"
) else if "!INSTALL_TYPE!" == "development" (
    call :print_info "Installing development dependencies..."
    uv pip install -r requirements.txt
    if !errorlevel! neq 0 (
        call :print_error "Failed to install core dependencies. Please check the error message above."
        pause
        exit /b 1
    )
    
    REM Install additional development tools
    uv pip install pytest black flake8
    if !errorlevel! neq 0 (
        call :print_warning "Failed to install some development tools. Continuing with core installation."
    ) else (
        call :print_success "Development dependencies installed"
    )
) else (
    call :print_info "Installing full dependencies..."
    uv pip install -r requirements.txt
    if !errorlevel! neq 0 (
        call :print_error "Failed to install full dependencies. Please check the error message above."
        pause
        exit /b 1
    )
    call :print_success "Full dependencies installed"
)

echo.

REM Create configuration file
call :print_info "Creating configuration file..."
call :create_checkpoint "create_config"

if not exist config\config.example.toml (
    call :print_error "config/config.example.toml not found."
    pause
    exit /b 1
)

copy config\config.example.toml config\config.toml >nul
if !errorlevel! neq 0 (
    call :print_error "Failed to create configuration file. Please check the error message above."
    pause
    exit /b 1
)

call :print_success "Configuration file created: config/config.toml"

if "!INTERACTIVE_MODE!" == "true" (
    call :configure_interactive
) else (
    call :print_info "Please edit config/config.toml to add your API keys and customize settings."
)

echo.

REM Verify installation
call :print_info "Verifying installation..."
call :create_checkpoint "verify_installation"

if not exist main.py (
    call :print_error "main.py not found. Installation may be incomplete."
    pause
    exit /b 1
)

python -c "import src.config" >nul 2>&1
if !errorlevel! neq 0 (
    call :print_warning "Some Python modules could not be imported. There might be an issue with the installation."
) else (
    call :print_success "Python modules imported successfully"
)

REM Run basic functionality test
call :print_info "Running basic functionality test..."
python -c "from src.agent.base import BaseAgent; print('BaseAgent imported successfully')" >nul 2>&1
if !errorlevel! neq 0 (
    call :print_warning "Core components verification failed"
) else (
    call :print_success "Core components verified"
)

call :print_success "Installation verification completed"

echo.
call :print_success "=== Installation Completed Successfully ==="
echo.
call :print_info "Next steps:"
call :print_info "1. Edit config/config.toml to add your API keys and customize settings"
call :print_info "2. Activate the virtual environment: .venv\Scripts\activate.bat"
call :print_info "3. Run the application: python main.py STOCK_CODE"
echo.
call :print_info "Example: python main.py 000001"
echo.
call :print_info "For more information, please read the INSTALLATION_GUIDE.md file."
call :print_info "Installation log saved to: %LOG_FILE%"
echo.
pause

exit /b 0

REM Function for interactive configuration
:configure_interactive
call :print_info "Starting interactive configuration..."

set /p API_TYPE="Enter your LLM API type (openai/azure/ollama) [openai]: "
if "!API_TYPE!" == "" set API_TYPE=openai

set /p MODEL_NAME="Enter your LLM model name [gpt-4o]: "
if "!MODEL_NAME!" == "" set MODEL_NAME=gpt-4o

powershell -Command "[System.Console]::Write('Enter your API key (input will be hidden): '); $pwd = Read-Host -AsSecureString; $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($pwd); $api_key = [System.Runtime.InteropServices.Marshal]::PtrToStringUni($ptr); [System.Runtime.InteropServices.Marshal]::ZeroFreeCoTaskMemUnicode($ptr); Write-Output $api_key" > .api_key_temp
set /p API_KEY=<.api_key_temp
del .api_key_temp >nul 2>&1

if not "!API_KEY!" == "" (
    REM Update config file with user inputs
    powershell -Command "(Get-Content config/config.toml) -replace 'api_type = \".*\"', 'api_type = \"%API_TYPE%\"' | Set-Content config/config.toml"
    powershell -Command "(Get-Content config/config.toml) -replace 'model = \".*\"', 'model = \"%MODEL_NAME%\"' | Set-Content config/config.toml"
    powershell -Command "(Get-Content config/config.toml) -replace 'api_key = \".*\"', 'api_key = \"%API_KEY%\"' | Set-Content config/config.toml"
    call :print_success "Configuration updated with your settings"
) else (
    call :print_info "No API key provided. Please edit config/config.toml manually."
)
exit /b
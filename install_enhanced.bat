@echo off
REM FinGenius 自动安装启动脚本 (增强版)
REM 此脚本会检查 Python 是否安装，然后启动自动安装程序

echo === FinGenius 自动安装启动 (增强版) ===
echo.

REM 检查 Python 是否安装
where /q python >nul 2>&1
if %errorlevel% neq 0 (
    echo X 未检测到 Python
    echo 请安装 Python 3.12 或更高版本后重新运行此脚本
    pause
    exit /b 1
)

echo √ 检测到 Python

REM 检查 Python 版本
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ℹ Python 版本: %PYTHON_VERSION%

REM 检查是否有参数
set ARGS=
if "%1"=="--no-progress" (
    set ARGS=--no-progress
    echo ⚠️ 已禁用进度显示
)

if "%1"=="--skip-tests" set ARGS=%ARGS% --skip-tests
if "%2"=="--skip-tests" set ARGS=%ARGS% --skip-tests
if "%1"=="--skip-tests" echo ⚠️ 已禁用安装测试
if "%2"=="--skip-tests" echo ⚠️ 已禁用安装测试

echo.
echo ℹ 开始安装过程...
echo.

REM 运行自动安装脚本
python auto_install_enhanced.py %ARGS%
pause
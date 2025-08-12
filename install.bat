@echo off
REM FinGenius 自动安装启动脚本
REM 此脚本会检查 Python 是否安装，然后启动自动安装程序

echo === FinGenius 自动安装启动 ===
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
REM 运行自动安装脚本
python auto_install.py
pause
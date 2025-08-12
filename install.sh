#!/bin/bash

# FinGenius 自动安装启动脚本
# 此脚本会检查 Python 是否安装，然后启动自动安装程序

echo "=== FinGenius 自动安装启动 ==="
echo ""

# 检查 Python 是否安装
if command -v python3 >/dev/null 2>&1; then
    echo "✓ 检测到 Python"
    # 给 auto_install.py 添加执行权限
    chmod +x auto_install.py
    # 运行自动安装脚本
    ./auto_install.py
else
    echo "✗ 未检测到 Python"
    echo "请安装 Python 3.12 或更高版本后重新运行此脚本"
    exit 1
fi
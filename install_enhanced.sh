#!/bin/bash

# FinGenius 自动安装启动脚本 (增强版)
# 此脚本会检查 Python 是否安装，然后启动自动安装程序

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}=== FinGenius 自动安装启动 (增强版) ===${NC}"
echo ""

# 检查 Python 是否安装
if command -v python3 >/dev/null 2>&1; then
    echo -e "${GREEN}✓ 检测到 Python${NC}"
    
    # 检查 Python 版本
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo -e "${BLUE}ℹ Python 版本: ${PYTHON_VERSION}${NC}"
    
    # 检查是否有参数
    ARGS=""
    if [ "$1" == "--no-progress" ]; then
        ARGS="--no-progress"
        echo -e "${YELLOW}⚠️ 已禁用进度显示${NC}"
    fi
    
    if [ "$1" == "--skip-tests" ] || [ "$2" == "--skip-tests" ]; then
        ARGS="$ARGS --skip-tests"
        echo -e "${YELLOW}⚠️ 已禁用安装测试${NC}"
    fi
    
    # 给 auto_install_enhanced.py 添加执行权限
    chmod +x auto_install_enhanced.py
    
    echo ""
    echo -e "${BLUE}ℹ 开始安装过程...${NC}"
    echo ""
    
    # 运行自动安装脚本
    ./auto_install_enhanced.py $ARGS
else
    echo -e "${RED}✗ 未检测到 Python${NC}"
    echo -e "${RED}请安装 Python 3.12 或更高版本后重新运行此脚本${NC}"
    exit 1
fi
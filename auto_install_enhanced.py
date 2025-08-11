#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FinGenius 自动安装脚本 (增强版)
此脚本会自动检测操作系统并执行相应的安装流程，
并提供进度显示和更好的错误处理
"""

import os
import sys
import time
import platform
import subprocess
import shutil
import argparse
from pathlib import Path

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# 进度条类
class ProgressBar:
    def __init__(self, total=100, prefix='', suffix='', decimals=1, length=50, fill='█', print_end="\r"):
        """
        初始化进度条
        @params:
            total       - 总迭代次数
            prefix      - 前缀字符串
            suffix      - 后缀字符串
            decimals    - 百分比小数位数
            length      - 进度条长度
            fill        - 进度条填充字符
            print_end   - 打印结束字符
        """
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.print_end = print_end
        self.iteration = 0
        self._print_progress()
    
    def update(self, iteration=None):
        """
        更新进度条
        @params:
            iteration  - 当前迭代次数
        """
        if iteration is not None:
            self.iteration = iteration
        else:
            self.iteration += 1
        self._print_progress()
    
    def _print_progress(self):
        """打印进度条"""
        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (self.iteration / float(self.total)))
        filled_length = int(self.length * self.iteration // self.total)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)
        print(f'\r{self.prefix} |{bar}| {percent}% {self.suffix}', end=self.print_end)
        # 如果完成则打印新行
        if self.iteration == self.total:
            print()

def print_header(message):
    """打印带颜色的标题"""
    print(f"{Colors.HEADER}{Colors.BOLD}=== {message} ==={Colors.ENDC}")

def print_success(message):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_warning(message):
    """打印警告信息"""
    print(f"{Colors.WARNING}⚠️ {message}{Colors.ENDC}")

def print_error(message):
    """打印错误信息"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    """打印普通信息"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")

def check_python_version():
    """检查 Python 版本是否满足要求"""
    print_info("检查 Python 版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 12):
        print_error(f"Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print_error("FinGenius 需要 Python 3.12 或更高版本")
        return False
    
    print_success(f"Python 版本兼容: {version.major}.{version.minor}.{version.micro}")
    return True

def command_exists(command):
    """检查命令是否存在"""
    return shutil.which(command) is not None

def install_uv():
    """安装 uv 包管理器"""
    print_info("安装 uv 包管理器...")
    
    if command_exists("uv"):
        print_success("uv 已安装")
        return True
    
    system = platform.system().lower()
    
    try:
        if system == "windows":
            # Windows 安装方式
            subprocess.run(
                ["powershell", "-c", "irm https://astral.sh/uv/install.ps1 | iex"],
                check=True
            )
        else:
            # macOS 和 Linux 安装方式
            if command_exists("curl"):
                subprocess.run(
                    ["curl", "-LsSf", "https://astral.sh/uv/install.sh", "|", "sh"],
                    check=True,
                    shell=True
                )
            elif command_exists("wget"):
                subprocess.run(
                    ["wget", "-O", "-", "https://astral.sh/uv/install.sh", "|", "sh"],
                    check=True,
                    shell=True
                )
            else:
                print_error("需要 curl 或 wget 来安装 uv")
                return False
        
        # 检查是否安装成功
        if not command_exists("uv"):
            # 尝试添加到 PATH
            home = Path.home()
            os.environ["PATH"] += os.pathsep + str(home / ".local" / "bin")
            
            if not command_exists("uv"):
                print_warning("uv 已安装但不在 PATH 中")
                print_warning("请重启终端或手动将 ~/.local/bin 添加到 PATH")
                return False
        
        print_success("uv 安装完成")
        return True
    
    except subprocess.CalledProcessError as e:
        print_error(f"安装 uv 失败: {e}")
        return False

def create_virtual_environment():
    """创建虚拟环境"""
    print_info("创建虚拟环境...")
    
    try:
        subprocess.run(["uv", "venv", "--python", "3.12"], check=True)
        print_success("虚拟环境创建成功")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"创建虚拟环境失败: {e}")
        return False

def activate_virtual_environment():
    """激活虚拟环境"""
    print_info("激活虚拟环境...")
    
    system = platform.system().lower()
    venv_path = None
    
    if system == "windows":
        venv_path = os.path.join(".venv", "Scripts", "activate.bat")
    else:
        venv_path = os.path.join(".venv", "bin", "activate")
    
    if not os.path.exists(venv_path):
        print_error(f"虚拟环境激活脚本不存在: {venv_path}")
        return False
    
    # 返回激活命令，而不是直接激活
    # 因为 Python 脚本无法直接修改父进程的环境
    if system == "windows":
        print_success("虚拟环境准备就绪")
        print_info(f"请使用命令激活虚拟环境: .venv\\Scripts\\activate.bat")
    else:
        print_success("虚拟环境准备就绪")
        print_info(f"请使用命令激活虚拟环境: source .venv/bin/activate")
    
    return True

def install_dependencies(show_progress=True):
    """安装项目依赖"""
    print_info("安装项目依赖...")
    
    if not os.path.exists("requirements.txt"):
        print_error("requirements.txt 文件不存在")
        return False
    
    try:
        # 使用 uv 安装依赖
        if show_progress:
            # 计算依赖数量
            with open("requirements.txt", "r") as f:
                dependencies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            # 创建进度条
            progress = ProgressBar(len(dependencies), prefix='安装进度:', suffix='完成', length=50)
            
            # 逐个安装依赖
            for i, dep in enumerate(dependencies):
                subprocess.run(["uv", "pip", "install", dep], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL, 
                               check=True)
                progress.update(i + 1)
                time.sleep(0.1)  # 添加短暂延迟以便看到进度
        else:
            # 一次性安装所有依赖
            subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], check=True)
        
        print_success("依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"安装依赖失败: {e}")
        return False

def create_config():
    """创建配置文件"""
    print_info("创建配置文件...")
    
    config_example = os.path.join("config", "config.example.toml")
    config_file = os.path.join("config", "config.toml")
    
    if not os.path.exists(config_example):
        print_error(f"{config_example} 文件不存在")
        return False
    
    try:
        # 复制配置文件
        shutil.copy2(config_example, config_file)
        print_success(f"配置文件已创建: {config_file}")
        print_info("请编辑此文件添加您的 API 密钥和自定义设置")
        return True
    except Exception as e:
        print_error(f"创建配置文件失败: {e}")
        return False

def create_mcp_config():
    """创建 MCP 配置文件"""
    print_info("创建 MCP 配置文件...")
    
    mcp_example = os.path.join("config", "mcp.example.json")
    mcp_file = os.path.join("config", "mcp.json")
    
    if not os.path.exists(mcp_example):
        print_warning(f"{mcp_example} 文件不存在，跳过 MCP 配置")
        return True
    
    try:
        # 复制配置文件
        shutil.copy2(mcp_example, mcp_file)
        print_success(f"MCP 配置文件已创建: {mcp_file}")
        return True
    except Exception as e:
        print_error(f"创建 MCP 配置文件失败: {e}")
        return False

def verify_installation():
    """验证安装"""
    print_info("验证安装...")
    
    if not os.path.exists("main.py"):
        print_error("main.py 文件不存在，安装可能不完整")
        return False
    
    try:
        # 尝试导入项目模块
        subprocess.run([sys.executable, "-c", "import src.config"], check=True)
        print_success("Python 模块导入成功")
    except subprocess.CalledProcessError:
        print_warning("部分 Python 模块无法导入，安装可能存在问题")
    
    print_success("安装验证完成")
    return True

def run_tests():
    """运行安装测试"""
    print_info("运行安装测试...")
    
    if not os.path.exists("test_easy_installation.py"):
        print_warning("test_easy_installation.py 文件不存在，跳过测试")
        return True
    
    try:
        # 运行测试
        subprocess.run([sys.executable, "test_easy_installation.py"], check=True)
        print_success("安装测试通过")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"安装测试失败: {e}")
        return False

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="FinGenius 自动安装脚本")
    parser.add_argument("--no-progress", action="store_true", help="不显示进度条")
    parser.add_argument("--skip-tests", action="store_true", help="跳过安装测试")
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    print_header("FinGenius 自动安装")
    print("此脚本将安装 FinGenius 项目及其所有依赖")
    print()
    
    # 检查 Python 版本
    if not check_python_version():
        print()
        print_error("请安装 Python 3.12 或更高版本后重新运行此脚本")
        sys.exit(1)
    
    print()
    
    # 安装 uv
    if not install_uv():
        print()
        print_error("请手动安装 uv 后重新运行此脚本")
        sys.exit(1)
    
    print()
    
    # 创建虚拟环境
    if not create_virtual_environment():
        print()
        print_error("请检查上述错误信息")
        sys.exit(1)
    
    print()
    
    # 激活虚拟环境
    if not activate_virtual_environment():
        print()
        print_error("请检查上述错误信息")
        sys.exit(1)
    
    print()
    
    # 安装依赖
    if not install_dependencies(not args.no_progress):
        print()
        print_error("请检查上述错误信息")
        sys.exit(1)
    
    print()
    
    # 创建配置文件
    if not create_config():
        print()
        print_error("请检查上述错误信息")
        sys.exit(1)
    
    print()
    
    # 创建 MCP 配置文件
    if not create_mcp_config():
        print()
        print_warning("MCP 配置创建失败，但这不影响基本功能")
    
    print()
    
    # 验证安装
    if not verify_installation():
        print()
        print_warning("安装验证失败，请检查上述错误信息")
    
    print()
    
    # 运行测试
    if not args.skip_tests:
        if not run_tests():
            print()
            print_warning("安装测试失败，但安装过程可能已成功完成")
    
    print()
    print_header("安装成功完成")
    print()
    print("后续步骤:")
    print("1. 编辑 config/config.toml 文件，添加您的 API 密钥和自定义设置")
    
    # 根据操作系统提供不同的激活命令
    if platform.system().lower() == "windows":
        print("2. 激活虚拟环境: .venv\\Scripts\\activate.bat")
    else:
        print("2. 激活虚拟环境: source .venv/bin/activate")
    
    print("3. 运行应用程序: python main.py STOCK_CODE")
    print()
    print("示例: python main.py 000001")
    print()
    print("更多信息，请阅读 INSTALLATION_GUIDE.md 文件")

if __name__ == "__main__":
    main()
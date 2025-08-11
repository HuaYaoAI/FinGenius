#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FinGenius 安装测试脚本
此脚本用于测试自动安装过程是否成功
"""

import os
import sys
import platform
import subprocess
import unittest
from pathlib import Path

class InstallationTest(unittest.TestCase):
    """测试安装过程"""
    
    def test_python_version(self):
        """测试 Python 版本是否满足要求"""
        version = sys.version_info
        self.assertGreaterEqual(version.major, 3, "Python 主版本号应大于等于 3")
        if version.major == 3:
            self.assertGreaterEqual(version.minor, 12, "Python 次版本号应大于等于 12")
    
    def test_uv_installation(self):
        """测试 uv 是否已安装"""
        # 检查 uv 是否在 PATH 中
        uv_path = self.which("uv")
        self.assertIsNotNone(uv_path, "uv 未安装或不在 PATH 中")
    
    def test_virtual_environment(self):
        """测试虚拟环境是否存在"""
        venv_dir = Path(".venv")
        self.assertTrue(venv_dir.exists(), "虚拟环境目录不存在")
        
        # 检查虚拟环境激活脚本
        if platform.system().lower() == "windows":
            activate_script = venv_dir / "Scripts" / "activate.bat"
        else:
            activate_script = venv_dir / "bin" / "activate"
        
        self.assertTrue(activate_script.exists(), "虚拟环境激活脚本不存在")
    
    def test_config_file(self):
        """测试配置文件是否存在"""
        config_file = Path("config") / "config.toml"
        self.assertTrue(config_file.exists(), "配置文件不存在")
    
    def test_main_script(self):
        """测试主脚本是否存在"""
        main_script = Path("main.py")
        self.assertTrue(main_script.exists(), "主脚本不存在")
    
    def test_module_import(self):
        """测试模块导入"""
        try:
            # 尝试导入项目模块
            result = subprocess.run(
                [sys.executable, "-c", "import src.config"],
                capture_output=True,
                text=True
            )
            self.assertEqual(result.returncode, 0, f"模块导入失败: {result.stderr}")
        except Exception as e:
            self.fail(f"模块导入测试失败: {e}")
    
    @staticmethod
    def which(cmd):
        """查找命令路径"""
        # 检查命令是否存在
        if platform.system().lower() == "windows":
            cmd = cmd + ".exe"
        
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, cmd)
            if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
                return exe_file
        
        return None

def run_tests():
    """运行测试"""
    print("=== FinGenius 安装测试 ===")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    run_tests()
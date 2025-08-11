# FinGenius 增强版一键安装指南

本项目提供了增强版一键安装脚本，不仅可以自动检测您的操作系统并执行相应的安装流程，还提供了进度显示、更好的错误处理和安装测试功能。

## 系统要求

- Python 3.12 或更高版本
- 稳定的网络连接
- 足够的磁盘空间

## 增强版一键安装方法

### Windows 系统

1. 双击运行 `install_enhanced.bat` 文件
2. 按照屏幕提示完成安装

### macOS 或 Linux 系统

1. 打开终端
2. 进入项目目录
3. 执行以下命令：
   ```bash
   chmod +x install_enhanced.sh
   ./install_enhanced.sh
   ```
4. 按照屏幕提示完成安装

## 命令行参数

增强版安装脚本支持以下命令行参数：

- `--no-progress`: 禁用进度条显示
- `--skip-tests`: 跳过安装测试

示例：
```bash
# 禁用进度条
./install_enhanced.sh --no-progress

# 跳过安装测试
./install_enhanced.sh --skip-tests

# 同时使用两个参数
./install_enhanced.sh --no-progress --skip-tests
```

## 安装过程

增强版自动安装脚本将执行以下步骤：

1. 检查 Python 版本
2. 安装 uv 包管理器
3. 创建虚拟环境
4. 安装项目依赖（带进度显示）
5. 创建配置文件
6. 创建 MCP 配置文件（如果存在）
7. 验证安装
8. 运行安装测试

## 安装后配置

安装完成后，您需要：

1. 编辑 `config/config.toml` 文件，添加您的 API 密钥和自定义设置
2. 激活虚拟环境：
   - Windows: `.venv\Scripts\activate.bat`
   - macOS/Linux: `source .venv/bin/activate`
3. 运行应用程序：`python main.py STOCK_CODE`

例如：`python main.py 000001`

## 增强功能

相比基础版安装脚本，增强版提供了以下额外功能：

1. **进度显示**：安装依赖时显示进度条
2. **彩色输出**：使用彩色文本增强可读性
3. **命令行参数**：支持自定义安装选项
4. **安装测试**：自动验证安装是否成功
5. **MCP 配置**：自动创建 MCP 配置文件（如果存在）

## 故障排除

如果在安装过程中遇到问题，请检查：

1. Python 版本是否为 3.12 或更高
2. 网络连接是否稳定
3. 是否有足够的磁盘空间
4. 是否有足够的权限创建文件和目录

如果问题仍然存在，请参考 `INSTALLATION_GUIDE.md` 文件中的详细说明，或在项目的 GitHub 仓库中提交 issue。

## 手动安装

如果您更喜欢手动安装，或者自动安装脚本出现问题，请参考 `INSTALLATION_GUIDE.md` 文件中的详细说明。
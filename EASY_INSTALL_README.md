# FinGenius 一键安装指南

本项目提供了一键安装脚本，可以自动检测您的操作系统并执行相应的安装流程，简化 FinGenius 项目的安装过程。

## 系统要求

- Python 3.12 或更高版本
- 稳定的网络连接
- 足够的磁盘空间

## 一键安装方法

### Windows 系统

1. 双击运行 `install.bat` 文件
2. 按照屏幕提示完成安装

### macOS 或 Linux 系统

1. 打开终端
2. 进入项目目录
3. 执行以下命令：
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
4. 按照屏幕提示完成安装

## 安装过程

自动安装脚本将执行以下步骤：

1. 检查 Python 版本
2. 安装 uv 包管理器
3. 创建虚拟环境
4. 安装项目依赖
5. 创建配置文件
6. 验证安装

## 安装后配置

安装完成后，您需要：

1. 编辑 `config/config.toml` 文件，添加您的 API 密钥和自定义设置
2. 激活虚拟环境：
   - Windows: `.venv\Scripts\activate.bat`
   - macOS/Linux: `source .venv/bin/activate`
3. 运行应用程序：`python main.py STOCK_CODE`

例如：`python main.py 000001`

## 故障排除

如果在安装过程中遇到问题，请检查：

1. Python 版本是否为 3.12 或更高
2. 网络连接是否稳定
3. 是否有足够的磁盘空间
4. 是否有足够的权限创建文件和目录

如果问题仍然存在，请参考 `INSTALLATION_GUIDE.md` 文件中的详细说明，或在项目的 GitHub 仓库中提交 issue。

## 手动安装

如果您更喜欢手动安装，或者自动安装脚本出现问题，请参考 `INSTALLATION_GUIDE.md` 文件中的详细说明。
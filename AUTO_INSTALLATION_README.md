# FinGenius 自动安装说明

本项目包含一个自动安装脚本，可以简化 FinGenius 项目的安装过程。

## 使用方法

1. 确保您的系统满足以下要求：
   - Python 3.12 或更高版本
   - curl 或 wget（用于下载 uv 包管理器）
   - Git（用于克隆仓库）

2. 运行自动安装脚本：
   ```bash
   ./install_fingenius.sh
   ```

3. 脚本将自动执行以下步骤：
   - 检查 Python 版本
   - 安装 uv 包管理器
   - 克隆 FinGenius 仓库
   - 创建虚拟环境
   - 安装项目依赖
   - 创建配置文件

4. 安装完成后，按照脚本输出的指示进行操作：
   - 编辑 `config/config.toml` 文件，添加您的 API 密钥和自定义设置
   - 激活虚拟环境：`source .venv/bin/activate`
   - 运行应用程序：`python main.py STOCK_CODE`

## 手动安装

如果您更喜欢手动安装，或者自动安装脚本出现问题，请参考 `INSTALLATION_GUIDE.md` 文件中的详细说明。

## 故障排除

如果在运行自动安装脚本时遇到问题，请检查以下几点：

1. 确保您的系统满足所有要求
2. 检查是否有足够的磁盘空间
3. 确保网络连接稳定
4. 查看脚本输出的错误信息

如果问题仍然存在，请在项目的 GitHub 仓库中提交 issue。
# FinGenius 自动安装指南

本指南将帮助您自动安装和配置 FinGenius 项目。FinGenius 是一个基于多智能体架构的 AI 金融分析平台，专为 A 股市场设计。

## 系统要求

- Python 3.12 或更高版本
- macOS、Linux 或 Windows 操作系统
- 稳定的网络连接

## 安装步骤

### 1. 安装 uv 包管理器

uv 是一个极快的 Python 包管理器，推荐用于安装 FinGenius 项目。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

或者，如果您使用的是 Windows 系统：

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 克隆项目仓库

```bash
git clone https://github.com/HuaYaoAI/FinGenius.git
cd FinGenius
```

### 3. 创建并激活虚拟环境

```bash
uv venv --python 3.12
source .venv/bin/activate  # Unix/macOS 系统
# Windows 系统使用：
# .venv\Scripts\activate
```

### 4. 安装项目依赖

```bash
uv pip install -r requirements.txt
```

这将安装所有必要的 Python 包，包括：
- streamlit
- asyncio
- pydantic
- aiohttp
- openai
- fastmcp
- pandas
- numpy
- matplotlib
- 以及其他必需的依赖项

### 5. 配置项目

#### 5.1 创建配置文件

```bash
cp config/config.example.toml config/config.toml
```

#### 5.2 配置 LLM API 密钥

编辑 `config/config.toml` 文件，添加您的 API 密钥和自定义设置：

```toml
# Global LLM configuration
[llm]
api_type = "openai"  # API类型，可以是 "openai", "azure" 或 "ollama"
model = "gpt-4o"     # 您要使用的 LLM 模型
base_url = "https://api.openai.com/v1"  # API 端点 URL
api_key = "sk-..."   # 您的 API 密钥
max_tokens = 4096    # 响应中的最大令牌数
temperature = 0.0    # 控制随机性
```

对于不同的 LLM 提供商，您可以使用以下配置：

**Azure OpenAI 配置示例：**
```toml
[llm]
api_type = "azure"
model = "YOUR_MODEL_NAME"
base_url = "{YOUR_AZURE_ENDPOINT.rstrip('/')}/openai/deployments/{AZURE_DEPOLYMENT_ID}"
api_key = "AZURE API KEY"
max_tokens = 8096
temperature = 0.0
api_version = "AZURE API VERSION"
```

**Ollama 配置示例：**
```toml
[llm]
api_type = "ollama"
model = "llama3.2"  # 例如: "llama3.2", "qwen2.5", "deepseek-coder"
base_url = "http://localhost:11434/v1"  # 您的 Ollama 服务地址
api_key = "ollama"  # 可以是任意值，Ollama 会忽略但 OpenAI SDK 需要
max_tokens = 4096
temperature = 0.0
```

#### 5.3 配置搜索引擎（可选）

在 `config/config.toml` 文件中，您可以配置搜索引擎：

```toml
[search]
# 搜索引擎，可以是 "Google", "Baidu", "DuckDuckGo" 或 "Bing"
engine = "Bing"
```

对于国内用户，建议使用以下搜索引擎优先级：
- Baidu（百度）- 国内访问最稳定
- Bing（必应）- 国际化且国内可用
- Google - 作为备选（需要良好的国际网络）
- DuckDuckGo - 作为备选（需要良好的国际网络）

### 6. 配置 MCP 服务器（可选）

如果您需要使用 MCP（Model Context Protocol）服务器，可以创建 `config/mcp.json` 文件：

```bash
cp config/mcp.example.json config/mcp.json
```

然后根据需要编辑 `config/mcp.json` 文件。

## 验证安装

要验证安装是否成功，可以运行以下命令：

```bash
python main.py 000001
```

这将对股票代码为 000001 的股票进行分析。您也可以使用其他参数：

```bash
# 启用文本转语音
python main.py 000001 --tts

# 设置3轮辩论
python main.py 000001 --debate-rounds 3

# 自定义输出格式并保存到文件
python main.py 000001 --format json --output analysis_report.json
```

## 常见问题解答

### Q: 安装过程中遇到权限问题怎么办？

A: 确保您有足够的权限在项目目录中创建文件和目录。如果遇到权限问题，可以尝试使用 `sudo` 命令（在 Unix/Linux/macOS 系统上）或以管理员身份运行命令提示符（在 Windows 上）。

### Q: 如何更新项目依赖？

A: 如果项目依赖有更新，可以运行以下命令：

```bash
uv pip install -r requirements.txt --upgrade
```

### Q: 如何退出虚拟环境？

A: 运行以下命令退出虚拟环境：

```bash
deactivate
```

## 故障排除

如果在安装或运行过程中遇到问题，请检查以下几点：

1. 确保 Python 版本为 3.12 或更高
2. 确保所有依赖项都已正确安装
3. 检查配置文件中的 API 密钥是否正确
4. 确保网络连接稳定

如果问题仍然存在，请查看项目的 GitHub 仓库中的 issues 部分，或创建新的 issue 来寻求帮助。
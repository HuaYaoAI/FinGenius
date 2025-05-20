<h1 align="center">FinGenius - 金融博弈智能体</h1>

<div align="center">
<img src="docs/logo.png" alt="logo" width="200">
</div>

<p align="center">
<img src="https://img.shields.io/badge/License-Apache%202.0-yellow.svg?style=flat-square" alt="License">
<img src="https://img.shields.io/badge/Python-3.12%2B-blue.svg?style=flat-square&logo=python" alt="Python">
<img src="https://img.shields.io/github/stars/huayaoyuanjin/FinGenius" alt="Stars">
<a href="https://fingenius.cn"><img src="https://img.shields.io/badge/Website-fingenius.cn-purple.svg?style=flat-square" alt="Website"></a>
</p>

## 项目简介

FinGenius 是一个开源的智能金融分析平台，采用 **Research–Battle 双子星环境多智能体架构**，融合大语言模型与专业金融工具（基于 MCP 协议）， 通过多个专业的 AI 金融分析师的协作研究与博弈对抗，深度提供上市公司的多角度和多维度的分析。

> 本项目仅供学习和研究，不构成任何投资建议。投资有风险，入市需谨慎。

![architecture](docs%2Farchitecture.png)

## APP体验

我们诚挚邀请您体验，团队6年的心血，FinGenius移动应用：

- 上架时间：本月底将正式登陆各大应用市场
- 支持平台：安卓应用商店、iOS App Store
- 特色功能：史上第一款，数学博弈魔法，革新A股体验场景。

让我们携手完善[FinGenius](https://fingenius.cn)，共同探索金融智能分析的技术前沿！🌟

## 安装指南

我们提供两种安装方式。推荐使用方式二（uv），因为它能提供更快的安装速度和更好的依赖管理。

### 方式一：使用 conda

1. 创建新的 conda 环境：

   ```bash
   conda create -n fingenius python=3.12
   conda activate fingenius
   ```

2. 克隆仓库：

   ```bash
   git clone https://github.com/huayaoyuanjin/FinGenius.git
   cd FinGenius
   ```

3. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

### 方式二：使用 uv（推荐）

1. 安装 uv（一个快速的 Python 包管理器）：

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. 克隆仓库：

   ```bash
   git clone https://github.com/huayaoyuanjin/FinGenius.git
   cd FinGenius
   ```

3. 创建并激活虚拟环境：

   ```bash
   uv venv --python 3.12
   source .venv/bin/activate  # Unix/macOS 系统
   # Windows 系统使用：
   # .venv\Scripts\activate
   ```

4. 安装依赖：

   ```bash
   uv pip install -r requirements.txt
   ```

## 配置说明

FinGenius 需要配置使用的 LLM API，请按以下步骤设置：

1. 在 `config` 目录创建 `config.toml` 文件（可从示例复制）：

   ```bash
   cp config/config.example.toml config/config.toml
   ```

2. 编辑 `config/config.toml` 添加 API 密钥和自定义设置：

   ```toml
   # 全局 LLM 配置
   [llm]
   model = "gpt-4o"
   base_url = "https://api.openai.com/v1"
   api_key = "sk-..."  # 替换为真实 API 密钥
   max_tokens = 4096
   temperature = 0.0

   # 可选特定 LLM 模型配置
   [llm.vision]
   model = "gpt-4o"
   base_url = "https://api.openai.com/v1"
   api_key = "sk-..."  # 替换为真实 API 密钥
   ```

## 使用方法

一行命令运行 FinGenius：

```bash
python main.py 股票代码
```

### 可选参数

- `-f, --format` - 输出格式（text 或 json）
- `-o, --output` - 将结果保存到文件
- `--tts` - 启用文本转语音播报最终结果
- `--max-steps` - 每个智能体的最大步数（默认: 3）

## 项目结构

FinGenius 的系统架构以分层解耦与模块化协同为核心，通过明确的接口规范，构建了一个既健壮稳定又易于扩展的智能分析平台。为更直观地展示其内部结构与运作逻辑，以下类图和流程图分别从静态类组织和动态执行流程两个维度进行呈现。

### 类图

```mermaid
classDiagram
    %%==========================
    %% 1. Agent 层次结构
    %%==========================
    class BaseAgent {
        <<abstract>>
        - name: str
        - description: Optional[str]
        - system_prompt: Optional[str]
        - next_step_prompt: Optional[str]
        - llm: LLM
        - memory: Memory
        - state: AgentState
        - max_steps: int
        - current_step: int
        + run(request: Optional[str]) str
        + step() str <<abstract>>
        + update_memory(role, content, **kwargs) None
        + reset_execution_state() None
    }
    class ReActAgent {
        <<abstract>>
        + think() bool <<abstract>>
        + act() str <<abstract>>
        + step() str
    }
    class ToolCallAgent {
        - available_tools: ToolCollection
        - tool_choices: ToolChoice
        - tool_calls: List~ToolCall~
        + think() bool
        + act() str
        + execute_tool(command: ToolCall) str
        + cleanup() None
    }
    class MCPAgent {
        - mcp_clients: MCPClients
        - tool_schemas: Dict~str, dict~
        - connected_servers: Dict~str, str~
        - initialized: bool
        + create(...) MCPAgent
        + initialize_mcp_servers() None
        + connect_mcp_server(url, server_id) None
        + initialize(...) None
        + _refresh_tools() Tuple~List~str~,List~str~~
        + cleanup() None
    }
    class SentimentAgent {
        <<extends MCPAgent>>
    }
    class RiskControlAgent {
        <<extends MCPAgent>>
    }
    class HotMoneyAgent {
        <<extends MCPAgent>>
    }
    class TechnicalAnalysisAgent {
        <<extends MCPAgent>>
    }
    class ReportAgent {
        <<extends MCPAgent>>
    }

    %% 继承关系
    BaseAgent <|-- ReActAgent
    ReActAgent <|-- ToolCallAgent
    ToolCallAgent <|-- MCPAgent
    MCPAgent <|-- SentimentAgent
    MCPAgent <|-- RiskControlAgent
    MCPAgent <|-- HotMoneyAgent
    MCPAgent <|-- TechnicalAnalysisAgent
    MCPAgent <|-- ReportAgent

    %% 组合关系
    BaseAgent *-- LLM               : llm
    BaseAgent *-- Memory            : memory
    MCPAgent *-- MCPClients         : mcp_clients

    %%==========================
    %% 2. 环境（Environment）架构
    %%==========================
    class BaseEnvironment {
        <<abstract>>
        - name: str
        - description: str
        - agents: Dict~str, BaseAgent~
        - max_steps: int
        + create(...) BaseEnvironment
        + register_agent(agent: BaseAgent) None
        + run(...) Dict~str,Any~ <<abstract>>
        + cleanup() None
    }
    class ResearchEnvironment {
        - analysis_mapping: Dict~str,str~
        - results: Dict~str,Any~
        + initialize() None
        + run(stock_code: str) Dict~str,Any~
        + cleanup() None
    }
    class BattleState {
        - active_agents: Dict~str,str~
        - voted_agents: Dict~str,str~
        - terminated_agents: Dict~str,bool~
        - battle_history: List~Dict~str,Any~~
        - vote_results: Dict~str,int~
        - battle_highlights: List~Dict~str,Any~~
        - battle_over: bool
        + add_event(type, agent_id, ...) Dict~str,Any~
        + record_vote(agent_id,vote) None
        + mark_terminated(agent_id,reason) None
    }
    class BattleEnvironment {
        - state: BattleState
        - tools: Dict~str,BaseTool~
        + initialize() None
        + register_agent(agent: BaseAgent) None
        + run(report: Dict~str,Any~) Dict~str,Any~
        + handle_speak(agent_id, content) ToolResult
        + handle_vote(agent_id, vote) ToolResult
        + cleanup() None
    }
    class EnvironmentFactory {
        + create_environment(env_type: EnvironmentType, agents, ...) BaseEnvironment
    }

    %% 继承与工厂
    BaseEnvironment <|-- ResearchEnvironment
    BaseEnvironment <|-- BattleEnvironment
    EnvironmentFactory ..> BaseEnvironment : creates
    %% 环境中包含 Agents 和 BattleState
    BaseEnvironment o-- BaseAgent      : agents
    BattleEnvironment *-- BattleState  : state

    %%==========================
    %% 3. 工具（Tool）抽象
    %%==========================
    class MCPClients {
        - sessions: Dict~str,ClientSession~
        - exit_stacks: Dict~str,AsyncExitStack~
        + connect_sse(url, server_id) None
        + connect_stdio(cmd, args, server_id) None
        + list_tools() ListToolsResult
        + disconnect(server_id) None
    }

    %%==========================
    %% 4. 支持类
    %%==========================
    class Memory {
        - messages: List~Message~
        + add_message(msg: Message) None
        + clear() None
    }
    class LLM {
        - model: str
        - max_tokens: int
        - temperature: float
        + ask(messages, system_msgs, ...) str
        + ask_tool(messages, tools, tool_choice, ...) Message
    }
```

### 流程图
```mermaid
sequenceDiagram
    %% 简化版 FinGenius 执行流程（Agent Team）
    participant User
    participant Main
    participant Env as Environment
    participant Agents as Agent Team
    participant Tool

    %% 用户发起股票研究
    User->>Main: run(stock_code)
    Main->>Env: create & run(stock_code)

    %% 研究阶段：Agent Team 循环分析并调用工具
    Env->>Agents: analyze(stock_code)
    loop 分析循环
        Agents->>Agents: step()/think()/act()
        Agents->>Tool: call tool
        Tool-->>Agents: 返回结果
    end
    Agents-->>Env: analysis result
    Env-->>Main: research results

    %% 博弈阶段：Agent Team 重置状态并循环参与
    Main->>Env: run battle with research results
    Env->>Agents: reset & run battle
    loop 博弈循环
        Agents->>Agents: step()/think()/act()
        Agents->>Tool: call battle tool
        Tool-->>Agents: 返回结果
    end
    Agents-->>Env: battle result
    Env-->>Main: final decision

    %% 输出最终结果
    Main-->>User: display results
```

## 许可证

FinGenius 使用 [Apache 2.0 许可证](LICENSE)。

## 致谢

本项目基于 OpenManus 多智能体框架开发，继承了其"工具即能力"的核心理念，并将其扩展到金融分析领域，打造出专业化的金融智能体团队。

感谢 [OpenManus](https://github.com/mannaandpoem/OpenManus) 项目的启发与支持。

特别感谢 [JayTing511](https://github.com/JayTing511) 对本项目的支持与帮助。

项目顾问：[mannaandpoem](https://github.com/mannaandpoem)

我们诚邀所有AI和金融领域的开发者与研究者加入FinGenius开源社区！

> ⚠️ 免责声明：本项目仅用于教育和研究目的，专注于金融分析技术的探索，不提供投资预测或决策建议。

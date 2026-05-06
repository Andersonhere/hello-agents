# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指导。

## 项目概述

Hello-Agents 是一本系统性的智能体学习教程，旨在从零开始构建 AI 智能体。内容涵盖智能体基础概念、经典范式（ReAct、Plan-and-Solve、Reflection）、框架开发（AutoGen、AgentScope、LangGraph）以及高级主题（记忆与检索、RAG、上下文工程、通信协议、强化学习训练、性能评估）。项目包含理论文档（`docs/`）和实践代码（`code/`）两部分。

## 环境配置

### Python 版本要求
- **Python 3.10+**（必需）

### 环境变量配置
将 `.env.example` 复制为 `.env` 并填写配置：

```env
# 统一 LLM 配置（框架自动检测提供商）
LLM_MODEL_ID=your-model-name
LLM_API_KEY=your-api-key-here
LLM_BASE_URL=your-api-base-url
LLM_TIMEOUT=60

# 可选：工具相关 API 密钥
TAVILY_API_KEY=your-tavily-key
SERPAPI_API_KEY=your-serpapi-key
GITHUB_PERSONAL_ACCESS_TOKEN=your-github-token
```

常用 LLM 提供商地址：
- AIHubmix: `https://aihubmix.com/v1`
- ModelScope: `https://api-inference.modelscope.cn/v1/`
- OpenAI: `https://api.openai.com/v1`

### 依赖安装
每个章节/项目有独立的 `requirements.txt`，按章节安装：

```bash
# 按章节安装
pip install -r code/chapterX/requirements.txt

# 项目示例
pip install -r code/chapter13/helloagents-trip-planner/backend/requirements.txt
```

### 虚拟环境（推荐）
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

## 运行代码示例

### 章节示例
大多数章节有可直接运行的独立 Python 文件：

```bash
# 第一章 - 首个智能体测试
cd code/chapter1
python FirstAgentTest.py

# 第四章 - 经典智能体范式（ReAct、Reflection、Plan-and-Solve）
cd code/chapter4
python ReAct.py
python Reflection.py
python Plan_and_solve.py

# 第七章 - 构建自定义框架
cd code/chapter7
python my_main.py
python test_react_agent.py
```

### 全栈项目
包含前后端的项目（第13、14、15章）：

```bash
# 后端
cd code/chapter13/helloagents-trip-planner/backend
pip install -r requirements.txt
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd code/chapter13/helloagents-trip-planner/frontend
npm install
npm run dev
```

### Jupyter Notebook
部分章节使用 `.ipynb` 文件，可在 Jupyter 或 VS Code 中打开。

## 核心框架：HelloAgents

自定义框架 `hello-agents` 是本教程的核心。主要组件：

```python
from hello_agents import SimpleAgent, HelloAgentsLLM, ReActAgent, ToolAwareSimpleAgent
from hello_agents.tools import MCPTool, ToolRegistry
from hello_agents.tools.builtin import NoteTool

# 基本用法
llm = HelloAgentsLLM()  # 自动从环境变量配置
agent = SimpleAgent(name="助手", llm=llm)
response = agent.run("你的问题")

# 使用 MCP 工具
mcp_tool = MCPTool(
    name="filesystem",
    server_command=["npx", "-y", "@modelcontextprotocol/server-filesystem", "."]
)
agent.add_tool(mcp_tool)
```

### 自定义 LLM 提供商
继承 `HelloAgentsLLM` 扩展自定义提供商（参考 `code/chapter7/my_llm.py`）：

```python
from hello_agents import HelloAgentsLLM

class MyLLM(HelloAgentsLLM):
    def __init__(self, provider: str = "auto", **kwargs):
        if provider == "modelscope":
            # 自定义提供商逻辑
            self.api_key = kwargs.get('api_key') or os.getenv("MODELSCOPE_API_KEY")
            self.base_url = "https://api-inference.modelscope.cn/v1/"
            # ... 使用这些配置初始化 OpenAI 客户端
        else:
            super().__init__(provider=provider, **kwargs)
```

## 项目架构

### 目录结构
```
docs/                    # 教程文档（中英文）
  ├── chapter1-16/       # 各章节 markdown 文件
  └── images/            # 各章节配图

code/                    # 实践代码示例
  ├── chapter1-4/        # 智能体基础概念与经典范式
  ├── chapter6/          # 框架演示（AutoGen、AgentScope、LangGraph、CAMEL）
  ├── chapter7/          # 构建自定义 HelloAgents 框架
  ├── chapter8/          # 记忆与 RAG 实现
  ├── chapter9/          # 上下文工程
  ├── chapter10/         # 通信协议（MCP、A2A、ANP）
  ├── chapter11/         # Agentic RL（SFT、GRPO 训练）
  ├── chapter12/         # 智能体评估（BFCL、GAIA 基准测试）
  ├── chapter13/         # 智能旅行助手项目（Vue3 + FastAPI + MCP）
  ├── chapter14/         # 深度研究智能体
  └── chapter15/         # 赛博小镇模拟（Godot + FastAPI）

Extra-Chapter/           # 社区贡献的补充内容

Co-creation-projects/    # 社区共创毕业设计项目
```

### 智能体经典范式（第四章）

1. **ReAct**：思考-行动-观察循环
2. **Plan-and-Solve**：任务分解，顺序执行
3. **Reflection**：自我反思与改进循环

### 通信协议（第十章）

- **MCP (Model Context Protocol)**：通过 `MCPTool` 集成工具
- **A2A (Agent-to-Agent)**：多智能体通信
- **ANP (Agent Network Protocol)**：任务分发与负载均衡

## 开发规范

### 代码风格
- Python 文件使用 `from dotenv import load_dotenv` 加载环境变量
- LLM 客户端遵循 OpenAI 兼容接口模式
- 工具具有标准化的 `run()` 方法，接受字典配置

### 添加新工具
```python
from hello_agents.tools import ToolRegistry

registry = ToolRegistry()
registry.register_tool(my_tool)  # 工具必须有 name、description、run() 属性
```

### 测试智能体实现
测试文件遵循 `test_*.py` 命名规范，位于各章节目录中。

## 常见问题

### API 密钥配置
如果出现 "API key not found" 错误：
1. 确保工作目录下存在 `.env` 文件
2. 检查环境变量名称是否与预期格式匹配
3. 验证 API 密钥有效且有配额

### 导入错误
如果 `from hello_agents import ...` 失败：
```bash
pip install hello-agents>=0.2.4,<=0.2.9
```

协议功能（MCP、A2A）需额外安装：
```bash
pip install "hello-agents[protocols]>=0.2.4,<=0.2.9"
```

### 章节特定依赖
每个章节可能需要不同的依赖包。运行代码前务必检查并安装该章节的 `requirements.txt`。

## 社区贡献

- `Extra-Chapter/`：补充教程（面试题总结、Dify 教程、GUI Agent 等）
- `Co-creation-projects/`：社区共建毕业设计项目，遵循 `{用户名}-{项目名}` 命名规范

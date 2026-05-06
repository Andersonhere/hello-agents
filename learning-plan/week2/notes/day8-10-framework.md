# Day 8-10 学习笔记：HelloAgents 框架核心

> 学习时间：2025-05-05
> 学习内容：HelloAgents 框架架构与核心类设计

---

## 一、框架架构总览

### 1.1 架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        HelloAgents 框架架构                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                        用户层 (Agent)                            │   │
│   │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │   │
│   │  │ SimpleAgent  │ │ ReActAgent   │ │ ReflectionAgent          │ │   │
│   │  │ 简单对话     │ │ 思考-行动    │ │ 反思改进                 │ │   │
│   │  └──────────────┘ └──────────────┘ └──────────────────────────┘ │   │
│   │  ┌──────────────┐ ┌──────────────┐                              │   │
│   │  │ PlanSolve    │ │ FunctionCall │                              │   │
│   │  │ 计划分解     │ │ 函数调用     │                              │   │
│   │  └──────────────┘ └──────────────┘                              │   │
│   └─────────────────────────────┬───────────────────────────────────┘   │
│                                 │                                       │
│   ┌─────────────────────────────↓───────────────────────────────────┐   │
│   │                        核心层 (Core)                             │   │
│   │  ┌──────────────┐ ┌──────────────┐ ┌──────────┐ ┌────────────┐  │   │
│   │  │HelloAgentsLLM│ │ ToolRegistry │ │  Config  │ │  Message   │  │   │
│   │  │ LLM客户端    │ │ 工具注册表   │ │  配置    │ │  消息      │  │   │
│   │  └──────────────┘ └──────────────┘ └──────────┘ └────────────┘  │   │
│   └─────────────────────────────┬───────────────────────────────────┘   │
│                                 │                                       │
│   ┌─────────────────────────────↓───────────────────────────────────┐   │
│   │                        工具层 (Tools)                            │   │
│   │  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌─────────────────┐   │   │
│   │  │SearchTool│ │Calculator│ │  NoteTool  │ │ TerminalTool    │   │   │
│   │  │ 搜索     │ │ 计算器   │ │  笔记      │ │ 终端           │   │   │
│   │  └──────────┘ └──────────┘ └────────────┘ └─────────────────┘   │   │
│   │  ┌──────────────────────────────────────────────────────────┐   │   │
│   │  │                     MCPTool                               │   │   │
│   │  │               (MCP 协议工具包装器)                         │   │   │
│   │  └──────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                     扩展层 (Extensions)                          │   │
│   │  ┌────────────┐ ┌──────────────┐ ┌───────────────┐              │   │
│   │  │  Memory    │ │     RAG      │ │  Evaluation   │              │   │
│   │  │  记忆系统  │ │  检索增强    │ │  评估基准     │              │   │
│   │  └────────────┘ └──────────────┘ └───────────────┘              │   │
│   │  ┌────────────┐ ┌──────────────┐ ┌───────────────┐              │   │
│   │  │ Protocols  │ │      RL      │ │   Context     │              │   │
│   │  │ MCP/A2A/ANP│ │  强化学习    │ │   上下文构建  │              │   │
│   │  └────────────┘ └──────────────┘ └───────────────┘              │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 模块职责

| 模块 | 职责 | 核心文件 |
|------|------|----------|
| **用户层** | 提供各种 Agent 实现范式 | `agents/*.py` |
| **核心层** | 基础抽象和配置管理 | `core/*.py` |
| **工具层** | 工具定义和执行 | `tools/*.py` |
| **扩展层** | 高级功能扩展 | `memory/`, `protocols/`, `rl/` |

---

## 二、核心类详解

### 2.1 HelloAgentsLLM - LLM 客户端封装

**位置**: `hello_agents/core/llm.py`

**作用**: 统一的 LLM 调用接口，支持多种提供商

```python
from hello_agents import HelloAgentsLLM

# 方式1：自动从环境变量加载
llm = HelloAgentsLLM()

# 方式2：指定提供商
llm = HelloAgentsLLM(provider="modelscope")

# 方式3：完全自定义
llm = HelloAgentsLLM(
    model="Qwen/Qwen2.5-72B-Instruct",
    api_key="your-api-key",
    base_url="https://api-inference.modelscope.cn/v1/"
)
```

**核心设计**：

```
┌─────────────────────────────────────────────────────────────┐
│                    HelloAgentsLLM                            │
├─────────────────────────────────────────────────────────────┤
│  属性：                                                      │
│  ├── model: str          # 模型名称                         │
│  ├── provider: str       # 提供商 (openai/deepseek/qwen...) │
│  ├── api_key: str        # API 密钥                         │
│  ├── base_url: str       # API 地址                         │
│  ├── temperature: float  # 温度参数                         │
│  └── _client: OpenAI     # OpenAI 客户端实例                │
├─────────────────────────────────────────────────────────────┤
│  方法：                                                      │
│  ├── think(messages)     # 流式调用（推荐）                 │
│  ├── invoke(messages)    # 非流式调用                       │
│  └── stream_invoke()     # think 的别名                     │
├─────────────────────────────────────────────────────────────┤
│  提供商自动检测：                                            │
│  1. 检查特定环境变量 (OPENAI_API_KEY 等)                    │
│  2. 根据 API Key 格式判断 (ms- → modelscope)                │
│  3. 根据 base_url 判断                                      │
│  4. 默认使用 LLM_* 环境变量                                  │
└─────────────────────────────────────────────────────────────┘
```

**支持的提供商**：

| Provider | 环境变量 | 默认 Base URL |
|----------|----------|---------------|
| `openai` | `OPENAI_API_KEY` | `https://api.openai.com/v1` |
| `deepseek` | `DEEPSEEK_API_KEY` | `https://api.deepseek.com` |
| `qwen` | `DASHSCOPE_API_KEY` | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `modelscope` | `MODELSCOPE_API_KEY` | `https://api-inference.modelscope.cn/v1/` |
| `kimi` | `KIMI_API_KEY` | `https://api.moonshot.cn/v1` |
| `zhipu` | `ZHIPU_API_KEY` | `https://open.bigmodel.cn/api/paas/v4` |
| `ollama` | `OLLAMA_HOST` | `http://localhost:11434/v1` |
| `auto` | `LLM_*` | 从 `LLM_BASE_URL` 读取 |

---

### 2.2 Agent 基类

**位置**: `hello_agents/core/agent.py`

**作用**: 所有 Agent 的抽象基类

```python
class Agent(ABC):
    """Agent基类"""

    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None
    ):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.config = config or Config()
        self._history: list[Message] = []

    @abstractmethod
    def run(self, input_text: str, **kwargs) -> str:
        """运行Agent - 子类必须实现"""
        pass
```

**设计要点**：
- `name`: Agent 名称，用于日志和调试
- `llm`: LLM 客户端实例
- `system_prompt`: 系统提示词
- `_history`: 消息历史记录

---

### 2.3 SimpleAgent - 简单对话 Agent

**位置**: `hello_agents/agents/simple_agent.py`

**作用**: 最基础的 Agent，支持工具调用

```
┌─────────────────────────────────────────────────────────────┐
│                    SimpleAgent                               │
├─────────────────────────────────────────────────────────────┤
│  继承: Agent                                                 │
├─────────────────────────────────────────────────────────────┤
│  新增属性：                                                  │
│  ├── tool_registry: ToolRegistry    # 工具注册表           │
│  └── enable_tool_calling: bool      # 是否启用工具调用     │
├─────────────────────────────────────────────────────────────┤
│  核心方法：                                                  │
│  ├── run(input_text) → str          # 执行对话             │
│  ├── add_tool(tool)                 # 添加工具             │
│  └── stream_run(input_text)         # 流式输出             │
├─────────────────────────────────────────────────────────────┤
│  工具调用格式：                                              │
│  [TOOL_CALL:tool_name:parameters]                           │
│  示例: [TOOL_CALL:search:Python编程]                        │
│       [TOOL_CALL:calculator:a=12,b=8]                       │
└─────────────────────────────────────────────────────────────┘
```

**执行流程**：

```
用户输入 → 构建消息(系统提示+历史+当前) → LLM调用
    ↓
检测工具调用 → 解析参数 → 执行工具 → 获取结果
    ↓
继续LLM调用 → 无工具调用 → 返回最终答案
```

---

### 2.4 ReActAgent - 推理行动 Agent

**位置**: `hello_agents/agents/react_agent.py`

**作用**: 实现 ReAct 范式（思考-行动-观察循环）

```
┌─────────────────────────────────────────────────────────────┐
│                    ReActAgent                                │
├─────────────────────────────────────────────────────────────┤
│  核心理念: Reasoning + Acting                                │
│                                                             │
│  循环流程：                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Thought: 思考分析问题                               │   │
│  │     ↓                                                │   │
│  │  Action: 选择并执行工具                              │   │
│  │     ↓                                                │   │
│  │  Observation: 观察工具返回结果                       │   │
│  │     ↓                                                │   │
│  │  [循环直到有足够信息]                                │   │
│  │     ↓                                                │   │
│  │  Finish: 给出最终答案                                │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  关键属性：                                                  │
│  ├── tool_registry: ToolRegistry    # 工具注册表           │
│  ├── max_steps: int                 # 最大执行步数         │
│  └── prompt_template: str           # 提示词模板           │
└─────────────────────────────────────────────────────────────┘
```

**提示词模板格式**：

```
Thought: 分析问题，确定需要什么信息
Action: tool_name[input] 或 Finish[最终答案]

示例：
Thought: 用户想了解天气，我需要搜索当前天气信息
Action: search[北京天气]

Thought: 搜索结果显示北京今天晴朗
Action: Finish[北京今天天气晴朗，气温25度]
```

---

### 2.5 ToolRegistry - 工具注册表

**位置**: `hello_agents/tools/registry.py`

**作用**: 管理工具的注册、查询和执行

```python
from hello_agents import ToolRegistry

# 创建注册表
registry = ToolRegistry()

# 方式1：注册 Tool 对象
registry.register_tool(my_tool)

# 方式2：直接注册函数
registry.register_function(
    name="calculator",
    description="数学计算工具",
    func=calculate_func
)

# 执行工具
result = registry.execute_tool("calculator", "1+2*3")

# 获取工具描述（用于构建提示词）
desc = registry.get_tools_description()
```

**工具注册流程**：

```
┌─────────────────────────────────────────────────────────────┐
│                    ToolRegistry                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  注册工具 ──────────────────────────────────────────────┐   │
│                                                         │   │
│  register_tool(tool)                                    │   │
│       │                                                 │   │
│       ├── 检查是否可展开 (expandable)                   │   │
│       │   └── 是 → 展开为多个子工具                     │   │
│       │                                                 │   │
│       └── 存入 _tools 字典                              │   │
│                                                         │   │
│  register_function(name, description, func)             │   │
│       │                                                 │   │
│       └── 存入 _functions 字典                          │   │
│                                                         │   │
├─────────────────────────────────────────────────────────────┤
│  执行工具 ──────────────────────────────────────────────┐   │
│                                                         │   │
│  execute_tool(name, input_text)                         │   │
│       │                                                 │   │
│       ├── 优先查找 _tools 中的 Tool 对象                │   │
│       │   └── tool.run({"input": input_text})           │   │
│       │                                                 │   │
│       └── 查找 _functions 中的函数                      │   │
│           └── func(input_text)                          │   │
│                                                         │   │
└─────────────────────────────────────────────────────────────┘
```

---

### 2.6 Message - 消息类

**位置**: `hello_agents/core/message.py`

**作用**: 封装对话消息

```python
from hello_agents import Message

# 创建消息
msg = Message("你好", "user")
msg = Message("你好！有什么可以帮你的？", "assistant")

# 转换为 OpenAI 格式
msg.to_dict()  # {"role": "user", "content": "你好"}
```

---

## 三、框架使用流程

### 3.1 基础使用

```python
from hello_agents import SimpleAgent, HelloAgentsLLM

# 1. 创建 LLM 客户端
llm = HelloAgentsLLM()

# 2. 创建 Agent
agent = SimpleAgent(
    name="助手",
    llm=llm,
    system_prompt="你是一个有帮助的助手。"
)

# 3. 运行
response = agent.run("你好！")
```

### 3.2 使用工具

```python
from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools.builtin import CalculatorTool

# 1. 创建工具注册表
registry = ToolRegistry()
registry.register_tool(CalculatorTool())

# 2. 创建带工具的 Agent
agent = SimpleAgent(
    name="助手",
    llm=HelloAgentsLLM(),
    tool_registry=registry
)

# 3. 运行
response = agent.run("帮我算一下 123 * 456")
```

### 3.3 使用 ReAct Agent

```python
from hello_agents import ReActAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools.builtin import SearchTool

# 1. 创建工具
registry = ToolRegistry()
registry.register_tool(SearchTool())

# 2. 创建 ReAct Agent
agent = ReActAgent(
    name="搜索助手",
    llm=HelloAgentsLLM(),
    tool_registry=registry,
    max_steps=5
)

# 3. 运行
response = agent.run("今天北京的天气怎么样？")
```

---

## 四、类依赖关系

```
                    ┌─────────────┐
                    │   Config    │
                    └──────┬──────┘
                           │
                    ┌──────↓──────┐
                    │ HelloAgents │
                    │     LLM     │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────↓────┐      ┌─────↓─────┐     ┌────↓────┐
    │ Message │      │   Agent   │     │  Tool   │
    └─────────┘      └─────┬─────┘     │Registry │
                          │           └────┬────┘
         ┌────────────────┼────────────────┤
         │                │                │
    ┌────↓─────┐    ┌─────↓─────┐    ┌────↓─────┐
    │  Simple  │    │   ReAct   │    │   Tool   │
    │  Agent   │    │   Agent   │    │  Objects │
    └──────────┘    └───────────┘    └──────────┘
```

---

## 五、框架设计亮点

### 5.1 统一的 LLM 接口

- **自动检测提供商**: 无需手动配置，根据 API Key 或 URL 自动识别
- **环境变量优先**: 支持 `LLM_*` 统一环境变量，简化配置
- **流式响应默认**: `think()` 方法默认流式输出，提升体验

### 5.2 灵活的工具系统

- **两种注册方式**: Tool 对象（推荐）或 函数（简便）
- **自动展开**: MCP 等工具可自动展开为多个子工具
- **智能参数解析**: 支持多种参数格式

### 5.3 可扩展的 Agent 范式

- **基类抽象**: `Agent` 基类定义统一接口
- **多种范式**: Simple/ReAct/Reflection/PlanSolve 等
- **易于自定义**: 继承基类即可创建新 Agent

---

## 六、待实践验证

- [ ] 运行 `my_llm.py` 验证自定义 LLM
- [ ] 运行 `my_simple_agent.py` 验证 SimpleAgent
- [ ] 运行 `my_react_agent.py` 验证 ReActAgent
- [ ] 创建自定义 Agent 实践

---

*笔记更新时间：2025-05-05*
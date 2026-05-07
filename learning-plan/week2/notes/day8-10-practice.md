# Day 8-10 实践记录

> 时间：2025-05-05
> 状态：进行中

---

## 实验环境

- Python: 3.13
- LLM: Qwen3-235B-A22B (scnet)
- 工作目录: `/Users/gaoqi/wkspace/hello-agents/learning-plan/workspace/code/chapter7/`

---

## 实验 1：LLM 连接测试

### 测试脚本
`test_llm_simple.py`

### 运行命令
```bash
source /Users/gaoqi/wkspace/hello-agents/learning-plan/workspace/venv/bin/activate
python test_llm_simple.py
```

### 运行结果
```
==================================================
测试 LLM 连接
==================================================
Model: Qwen3-235B-A22B
Base URL: https://api.scnet.cn/api/llm/v1
API Key: sk-Njk4LTExNDk5MDYzM...

测试非流式调用...
回答: 你好，我是Qwen3，阿里巴巴集团旗下的通义实验室自主研发的超大规模语言模型...

测试流式调用...
回答: 我是通义千问，阿里巴巴集团旗下的超大规模语言模型...

==================================================
LLM 连接测试成功!
==================================================
```

### 关键理解
1. **HelloAgentsLLM 本质是对 OpenAI 客户端的封装**
2. 支持两种调用方式：
   - `invoke()`: 非流式，返回完整响应
   - `think()`: 流式，逐步输出
3. 环境变量配置：`LLM_MODEL_ID`, `LLM_API_KEY`, `LLM_BASE_URL`

---

## 实验 2：SimpleAgent 核心功能

### 测试脚本
`test_simple_agent.py`

### 核心类实现

#### 1. SimpleHelloAgentsLLM
```python
class SimpleHelloAgentsLLM:
    def __init__(self):
        self.model = os.getenv("LLM_MODEL_ID")
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")
        self.client = OpenAI(...)

    def invoke(self, messages: list) -> str:
        # 非流式调用

    def think(self, messages: list):
        # 流式调用
```

#### 2. SimpleToolRegistry
```python
class SimpleToolRegistry:
    def register_function(self, name, description, func):
        # 注册工具

    def execute_tool(self, name, input_text) -> str:
        # 执行工具

    def get_tools_description(self) -> str:
        # 获取工具描述（用于提示词）
```

#### 3. SimpleAgent
```python
class SimpleAgent:
    def __init__(self, name, llm, system_prompt, tool_registry):
        # 初始化 Agent

    def run(self, input_text) -> str:
        # 1. 构建消息（系统提示 + 历史 + 当前输入）
        # 2. 调用 LLM
        # 3. 检查工具调用
        # 4. 执行工具并继续对话
        # 5. 返回最终响应
```

### 运行结果

#### 测试 1: 简单对话
```
🤖 智能助手 正在处理: 你好，请介绍一下你自己
✅ 智能助手 响应完成

回答: 你好！我是你的智能助手，专注于为你提供以下两种服务：
1. **数学计算**：可以帮你计算各种数学表达式...
2. **时间查询**：能快速获取全球主要城市的当前时间...
```

#### 测试 2: 数学计算（工具调用）
```
🤖 智能助手 正在处理: 帮我算一下 123 * 456 等于多少
🔧 检测到 1 个工具调用
   → calculator 结果: 123*456 = 56088
✅ 智能助手 响应完成

回答: 123 × 456 = **56,088**
```

#### 测试 3: 多轮对话
```
🤖 智能助手 正在处理: 我刚才问了什么问题？
✅ 智能助手 响应完成

回答: 你刚才的问题是："帮我算一下 123 * 456 等于多少"。
```

### 关键理解

1. **Agent 核心流程**：
   ```
   输入 → 构建消息 → LLM调用 → 检查工具 → 执行工具 → 继续对话 → 输出
   ```

2. **工具调用格式**：
   ```
   [TOOL_CALL:工具名:参数]
   示例: [TOOL_CALL:calculator:123*456]
   ```

3. **消息历史管理**：
   - `_history` 列表存储对话历史
   - 每次调用时将历史加入消息列表
   - 实现"记忆"功能

4. **系统提示增强**：
   - 基础提示 + 工具描述
   - 告诉 LLM 可用什么工具及调用格式

---

## 遇到的问题

### 问题 1: 缺少 huggingface_hub 模块

**错误信息**:
```
ModuleNotFoundError: No module named 'huggingface_hub'
```

**解决方案**:
创建简化测试脚本，避免导入完整的 `hello_agents` 框架，直接使用 OpenAI 客户端模拟核心功能。

**原因**:
`hello_agents` 框架的评估模块依赖 `huggingface_hub`，但网络下载较慢。为了快速验证核心功能，使用简化脚本绕过此依赖。

---

## 下一步

- [ ] 安装完整依赖后运行 `my_simple_agent.py`
- [ ] 运行 `my_react_agent.py` 验证 ReAct 范式
- [ ] 创建自定义 Agent 实践

---

# Day 9 对比官方 SimpleAgent

Q1. 工具调用
你的 MiniSimpleAgent 没工具能力。官方 SimpleAgent 大概率有工具支持吗？

如果有，你猜它把工具列表存在哪个属性里？
存放在system_prompt中
工具是怎么"被 LLM 看见"的？
通过提示词嵌入
Q2. 流式输出（streaming）
你的 run() 是同步阻塞——LLM 全部生成完才返回。 官方会支持流式吗？ 如果支持，run() 的返回值可能会变成什么类型？
官方支持流式，返回值变成一个共享对象
Q3. 错误处理
你的代码里 LLM 调用没有 try/except。 如果 LLM 超时 / 返回 None / API 限流，会怎样？官方会怎么处理？
直接报错，然后设置重试次数，进行重试
Q4. 系统提示词的位置
你把 system_prompt 直接写进 messages[0]。 官方可能怎么处理 system prompt？想想这两种设计哪种更灵活：

A：直接放 messages[0]（你的方式）
B：单独存为属性，每次 run 时动态拼到 messages 前面
每次都拼接会占用上下文。我觉得拼接到messages[0]比较合适

Q5. 多轮对话的"边界"
你的 messages 永远累加。如果跑 100 轮：

会出什么问题？（提示：模型有 context window）
官方有没有做"窗口截断" / "摘要压缩" / 什么都不做？
摘要压缩。

*更新时间：2025-05-05*
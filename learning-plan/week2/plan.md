# Week 2：HelloAgents 深入 + LangGraph 专攻

> **周期**：Day 8 - Day 14
> **主题**：吃透 HelloAgents 框架内部实现，掌握工业界主流 LangGraph
> **产出**：双框架实现同一个 ReAct Agent + 一篇对比博客（**简历素材**）

---

## 🎯 修订说明（v2）

相比初版，本周做了以下调整：

- ❌ **砍掉 AutoGen / AgentScope**：工业界 Agent 岗位 90% 用 LangGraph，聚焦才能学透
- ✅ **新增"手写极简版"环节**：先不看源码，自己写 50 行版本，再对比官方实现
- ✅ **新增"双框架实现同一问题"**：HelloAgents vs LangGraph 实现同一个 ReAct Agent
- ✅ **新增周博客产出**：博客即面试素材

---

## 📋 本周目标

| 目标 | 说明 | 验收标准 |
|------|------|----------|
| 吃透 HelloAgents | 不仅会用，能讲清内部实现 | 手写 50 行极简版 ReActAgent |
| 掌握 LangGraph 核心抽象 | StateGraph/Node/Edge/Checkpoint | 独立画出状态图并实现 |
| 双框架对比能力 | 理解不同抽象的取舍 | 同一 Agent 用两种框架实现 |
| 输出能力 | 把学习沉淀成可复用资产 | 1 篇对比博客 |

---

## 📅 每日计划

| 日期 | 主题 | 重点任务 |
|------|------|----------|
| Day 8 | HelloAgents 源码精读 | 重点读 `SimpleAgent`、`ReActAgent`、`ToolRegistry` 源码 |
| Day 9 | **手写极简版 SimpleAgent** | 不看源码，50 行内实现一个能跑的版本 |
| Day 10 | **手写极简版 ReActAgent** + 对比官方 | 跑通后逐行对比，列出差异 |
| Day 11 | LangGraph 入门 | StateGraph、Node、Edge、State Schema |
| Day 12 | LangGraph 进阶 | 条件边（conditional_edge）、checkpointer 持久化 |
| Day 13 | **双框架实现 ReAct Agent** | 同一问题、同一工具、两套实现 |
| Day 14 | **写对比博客 + 周复盘** | 800 字博客，发布到掘金/知乎 |

---

## 📚 核心知识点

### 1. HelloAgents 源码阅读重点

聚焦 3 个核心类，**不要泛读**：

| 类 | 关注点 | 自问 |
|----|--------|------|
| `HelloAgentsLLM` | 如何封装 OpenAI 协议、流式输出 | 不用框架我能写吗？ |
| `ReActAgent` | prompt 模板、循环退出条件、解析 LLM 输出 | Action 解析失败怎么 recover？ |
| `ToolRegistry` | 工具注册、参数 schema、调用分发 | 怎么把一个 Python 函数变成 LLM 可见的 tool？ |

### 2. LangGraph 核心概念（必须掌握）

```
┌──────────────────────────────────────────────────────┐
│              LangGraph 核心抽象                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│   State (TypedDict)  ← 全局状态，节点间传递           │
│                                                      │
│   Node (函数)        ← 接收 State，返回 State 更新    │
│                                                      │
│   Edge               ← 静态：A → B                    │
│   Conditional Edge   ← 动态：根据 State 决定下一步    │
│                                                      │
│   Checkpointer       ← 状态持久化（内存/SQLite）      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**最小示例需要会写**：
- 一个 `agent_node`（调 LLM）
- 一个 `tool_node`（执行工具）
- 一个 `should_continue` 条件边（根据 LLM 输出判断是否还要调工具）
- 加上 `MemorySaver` checkpointer

### 3. 双框架对比维度

实现完后填这张表，作为博客素材：

| 维度 | HelloAgents | LangGraph |
|------|-------------|-----------|
| 抽象层级 | 类继承 | 状态图 |
| 控制流 | 隐藏在 `run()` | 显式定义边 |
| 状态管理 | 类属性 | TypedDict |
| 持久化 | 自己实现 | checkpointer 内置 |
| 调试体验 | print/log | trace 视图 |
| 学习曲线 | 平缓 | 较陡 |
| 适合场景 | 简单 Agent | 复杂工作流 |

---

## 🛠️ 关键约束（基于你的环境）

- **只有 LLM key**：所有工具用 mock 数据或本地实现
  - 搜索 → `duckduckgo-search` 包（无需 key）或 mock
  - 计算器、时间工具 → 纯 Python
  - 文件读写 → 本地文件系统

---

## ✅ 验收清单

### 必须完成
- [ ] 读完 `HelloAgentsLLM` / `ReActAgent` / `ToolRegistry` 三个类源码并写 200 字摘要
- [ ] 手写 `mini_simple_agent.py`（≤50 行，能跑）
- [ ] 手写 `mini_react_agent.py`（≤80 行，能跑）
- [ ] LangGraph 跑通官方 ReAct quickstart
- [ ] 自己用 LangGraph 实现一个带 2 个工具的 ReAct Agent
- [ ] 同一问题（如"查某城市天气并写诗"）用两种框架各实现一遍
- [ ] **写一篇 800 字对比博客**，至少包含：双框架代码片段、对比表格、个人结论

### 加分项
- [ ] LangGraph 加上 SQLite checkpointer，重启后能恢复对话
- [ ] 画一张架构对比图（Excalidraw / draw.io）

---

## 📁 产出位置

- 极简版代码：`learning-plan/output/code/week2/mini_*.py`
- LangGraph 实践：`learning-plan/output/code/week2/langgraph_*.py`
- 对比博客：`learning-plan/output/notes/week2-framework-comparison.md`

---

## 🔗 资源

### 必读
- HelloAgents 源码：`code/chapter7/`
- [LangGraph 官方 Quickstart](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
- [LangGraph ReAct Agent 示例](https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch/)

### 对比阅读
- `docs/chapter6/第六章 框架开发实践.md`
- `docs/chapter7/第七章 构建你的Agent框架.md`

---

## 🎓 周回顾问题（Day 14 自测）

合上电脑，纸笔回答：

1. ReAct 循环在 HelloAgents 和 LangGraph 中分别如何"退出"？
2. LangGraph 的 `State` 和 HelloAgents 的"对话历史"本质区别是什么？
3. 如果让你给一个新人 5 分钟讲明白 LangGraph，你会画哪 3 个图？
4. 工业界为什么选 LangGraph？它解决了什么 HelloAgents 没解决的问题？

能流畅回答 = 通过本周。

---

*[返回总计划](../README.md)*

# Week 2 学习总结：HelloAgents 深入 + LangGraph 专攻

> **学习周期**：Day 8 - Day 14
> **完成日期**：2026-05-18
> **主题**：吃透 HelloAgents 框架内部实现，掌握工业界主流 LangGraph，输出对比博客

---

## 📊 完成情况

### 任务完成统计

| 阶段 | 内容 | 完成率 |
|------|------|--------|
| Day 8 | HelloAgents 源码精读（SimpleAgent/ReActAgent/ToolRegistry） | ✅ 100% |
| Day 9 | 手写极简版 SimpleAgent | ✅ 100% |
| Day 10 | 手写极简版 ReActAgent + 对比官方 | ✅ 100% |
| Day 11 | LangGraph 入门（StateGraph/Node/Edge/State） | ✅ 100% |
| Day 12 | LangGraph 进阶（Checkpointer + Time Travel） | ✅ 100% |
| Day 13 | 双框架对比（HelloAgents vs LangGraph） | ✅ 100% |
| Day 14 | 对比博客 + 周复盘 | ✅ 100% |

### 验收清单

- [x] 读完三个核心类源码并写笔记
- [x] 手写 `mini_simple_agent.py`（≤50 行）
- [x] 手写 `mini_react_agent.py`（≤80 行）
- [x] LangGraph 跑通三关（线性 / QA / ReAct）
- [x] LangGraph 实现带 2 工具的 ReAct Agent
- [x] 同一问题双框架各实现一遍 + 对比表
- [x] **写一篇对比博客**（约 1100 字，超出 800 字目标）
- [x] **加分项**：LangGraph 加 SQLite checkpointer，重启恢复对话
- [ ] 加分项：架构对比图（未做，时间不够）

---

## 🎯 学习目标达成情况

| 目标 | 达成 | 证据 |
|---|---|---|
| 吃透 HelloAgents（能讲清内部实现） | ✅ | 手写 80 行 mini_react_agent.py |
| 掌握 LangGraph 核心抽象 | ✅ | 独立画图 + 三关全过 |
| 双框架对比能力 | ✅ | day13_compare.py 跑出量化对比 |
| 输出能力（沉淀成可复用资产） | ✅ | 1 篇博客 + 7 篇 day notes |

---

## 📝 核心知识点

### 1. ReAct 范式的本质（Day 8-10）

**ReAct = SimpleAgent + 循环 + 工具调用**

- `Thought → Action → Observation` 三段式 prompt
- LLM 输出用正则解析 Action
- Observation 用 `user` role 塞回 messages
- 终止条件：`Finish[...]` 或 `max_iterations`
- 必须用 `stop=["Observation:"]` 防 LLM 自己编 Observation

### 2. LangGraph 三大抽象（Day 11）

| 抽象 | 是什么 | 关键特性 |
|---|---|---|
| **StateGraph** | 有状态计算 DAG | 节点函数都是 `state → dict` |
| **State** | TypedDict + Annotated reducer | reducer 决定字段更新语义（覆盖 vs 追加）|
| **Edge** | 节点间路由 | 普通边 + 条件边（`add_conditional_edges`）|

**核心 mental model**：节点是纯函数，控制流由数据结构（state + reducer）驱动。

### 3. Checkpointer 持久化（Day 12）

**state + thread_id + checkpointer 三位一体**：

- state 是"内容"
- thread_id 是"边界"
- checkpointer 是"存储引擎"

**接口同形 / 实现异化**：MemorySaver / SqliteSaver / Postgres / Redis 共用 `BaseCheckpointSaver` 接口，换存储零代码改动 → **策略模式 + 依赖倒置 + 依赖注入** 三件套。

### 4. Time Travel（Day 12）

LangGraph 把 Git 的演化模型搬到了 Agent state 上：

| Git | LangGraph |
|---|---|
| commit | checkpoint |
| SHA | checkpoint_id |
| branch | thread_id |
| `git log` | `get_state_history` |
| `git checkout <sha>` | `invoke(None, {cp_id})` |

**核心创新**：每个节点跑完**自动 commit**（Git 要手动）。

### 5. 框架范式对比（Day 13）

**State as first-class citizen vs 副作用**：

- HelloAgents 风格 = 命令式：state 是 `self.messages`，调试是黑盒
- LangGraph 风格 = 声明式：state 是显式 dict，调试是白盒

→ "用数据结构表达控制流，比用控制流操纵数据结构更可观测、可测试、可持久化"。

---

## 🧪 实践成果

### 代码产出（learning-plan/code/week2/）

| 文件 | 行数 | 核心 |
|---|---|---|
| `mini_simple_agent.py` | ~50 | Day 9 手写 SimpleAgent |
| `mini_react_agent.py` | ~235 (含调试) | Day 10 手写 ReActAgent |
| `langgraph_hello.py` | ~334 | Day 11 三关 (linear/QA/ReAct) |
| `langgraph_checkpoint.py` | ~271 | Day 12 三关 (Memory/Sqlite/Time travel) |
| `day13_compare.py` | ~190 | Day 13 双框架对比脚本 |

### 笔记产出（learning-plan/week2/notes/）

7 篇 day notes（合计约 7 万字，含代码示例和详细推导）：
- day8-framework.md（25KB，源码精读）
- day8-react-test.md
- day9-practice.md
- day10-practice.md
- day11-langgraph.md（15KB）
- day12-checkpoint.md（12KB）
- day13-compare.md（8KB）

### 博客产出

- `learning-plan/output/notes/week2-framework-comparison.md`（~1100 字）
- 标题：《写完同一个 Agent 两遍后，我才懂 LangGraph 在卷什么》
- 核心论点："3 行 vs 25 行 + 5 个坑"

---

## 🐛 高价值踩坑

### 坑 1：reducer 不区分"初始化"和"追加"

同一个 thread_id 第二次跑 `invoke({"messages":[system,user]})`，messages 会**重复追加 system+user**。

**根因**：`Annotated[list, operator.add]` reducer 永远是追加语义。

**长期记忆**：**一个 thread_id = 一次对话生命周期**。新对话用新 ID，延续对话只传增量 user message。

### 坑 2：state 字段拼写错框架不报错

LangGraph 的 TypedDict 是运行时 dict，写错字段名只是多一个不被消费的 key，节点拿不到默默走默认值。

**应对**：写完节点立刻 `print(state)` 验证字段存在；加 checkpointer 后这种 bug 会被持久化进 DB 更难发现。

### 坑 3：tuple 单元素陷阱

```python
tools_call = len([...]),   # 行尾这个 , 让它变成 (3,)
tools_call + 1             # tuple + int → TypeError
```

**永久教训**：Python 行尾的 `,` 不是格式化空格，是语法。

### 坑 4：HelloAgents 风格"暴露内部状态"是范式硬伤

为了拿 metrics 必须改 `messages` 为 `self.messages`，看似 1 行改动，实际是**打破封装**。

LangGraph 版直接 `result["messages"]`，**0 改动**。

→ 这就是 Day 13 博客最大卖点：**可观测性是范式选择的副产品**。

---

## 🎓 总复盘 — Week 2 三大顿悟

### 顿悟 1：选框架不看 hello world

简单 demo 阶段两版打平（83 行 vs 73 行，46s vs 49s）。
**真正差异在加第三个需求时**：拿 metrics、加持久化、做 A/B、HITL …

### 顿悟 2：State 一等公民是范式革命

声明式 vs 命令式 ≠ 语法糖差异。
是"调试基本靠 print" vs "调试可以 time travel" 的代际差。

### 顿悟 3：工程框架的护城河 = 替你踩坑

LangGraph checkpointer = 3 行业务代码 + 替你处理 5 个工程难题（序列化/原子写/并发/thread 隔离/HITL）。

**类比**：用 SQLAlchemy 不是为了少打字，是为了别在 SQL 注入上栽跟头。

---

## 🔄 与 Week 1 的对比

| 维度 | Week 1 | Week 2 |
|---|---|---|
| **重点** | 概念理解 + 范式认知 | 框架内部 + 工程取舍 |
| **代码量** | 跑通示例为主 | 手写 + 双框架双实现 |
| **产出** | 笔记为主 | 笔记 + 代码 + 博客 |
| **关键词** | ReAct / Plan / Reflection | StateGraph / Checkpointer / 范式 |

Week 1 学"是什么"，Week 2 学"怎么选 / 为什么这样选"。

---

## 📌 待办与遗留

- [ ] 博客发布到掘金/知乎（Week 3 可做）
- [ ] LangGraph 架构对比图（Excalidraw，时间紧没做）
- [ ] `langgraph_hello.py` 的 `system_prompt` 风格统一（Day 12 提到的小重构）
- [ ] HelloAgents 实现 LangGraph Studio 风格的可视化调试器（练手项目候选）

---

## ⏭️ Week 3 展望

Week 2 学完了"工业框架的核心"，Week 3 可能方向（待 plan.md 更新）：

- **Multi-Agent**：从单 Agent 走向多 Agent 协作（LangGraph 的 supervisor / swarm 模式）
- **RAG + Agent**：让 Agent 能查私有知识库
- **生产级特性**：observability（LangSmith / OpenTelemetry）、evals、prompt 版本管理
- **专项深入**：挑一个 Day 13 博客提到的"5 个红利"做深度实现

---

> **一句话总结 Week 2**：
> *80 行手写让你懂 ReAct 怎么跑；LangGraph 让你懂 ReAct 怎么扩。*

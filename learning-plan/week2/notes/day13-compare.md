# Day 13：双框架对比 — HelloAgents 风格 vs LangGraph 风格

> **日期**：2026-05-17
> **目标**：跑通同一问题，把差异量化为博客素材
> **统一问题**：北京和上海今天哪个更热？热多少度？再算一下这个温差的 3 倍是多少？

---

## 🎯 关卡

- 关卡 1: 跑两版收集 metrics
- 关卡 2: 填对比表
- 关卡 3: 回答 3 个分析题

---

## 📊 实测对比表（关卡 1+2 完成 ✅）

### 定性维度

| 维度 | HelloAgents 风格（MiniReActAgent） | LangGraph 风格（build_react_graph） |
|---|---|---|
| **抽象层级** | 类继承（OOP） | 状态图（声明式 DAG） |
| **控制流** | `while` 循环隐藏在 `run()` 内 | 节点 + 条件边显式定义 |
| **状态管理** | 局部变量 `messages`（或 `self.messages`） | `TypedDict ReActState` + reducer |
| **持久化** | 无（要自己存 / 加载 / 隔离 thread） | `checkpointer` 一行启用 |
| **调试体验** | print + 自己读 messages | `get_state_history()` 时间旅行 + 分叉重跑 |
| **学习曲线** | 平缓（会 Python 类就能写） | 较陡（要懂 reducer / state schema / 条件边） |
| **适合场景** | 单线性任务、demo、教学 | 多分支工作流、HITL、需要审计 |

### 定量数据（同一问题：北京和上海哪个更热 + 温差×3）

| 维度 | HelloAgents 风格 | LangGraph 风格 |
|---|---|---|
| **代码行数（核心主体）** | 83 行（mini_react_agent.py L109-204） | 73 行（langgraph_hello.py L193-282） |
| **耗时** | 46.45 s | 48.99 s |
| **ReAct 迭代轮数** | 3 | 3 |
| **工具调用次数** | 3（get_weather×2 + calculate×1） | 3（同左） |
| **最终 messages 条数** | 9 | 9 |
| **最终答案** | "上海比北京热，温差是5°C。温差的3倍是15°C" | "上海更热，比北京高 5°C。温差的 3 倍是 15°C" |

### 数据解读

- ✅ **答案语义一致**：两版都答对了"上海更热 / 温差 5°C / 3 倍 = 15°C"，仅措辞不同（来自 LLM 输出随机性）
- ✅ **过程一致**：tool_calls / messages 完全相同，证明两版做了同样的工作
- ⚖️ **代码量接近**：83 vs 73，差距 10 行内 —— 在 demo 这种简单场景看不出 LangGraph 的优势
- ⚖️ **耗时差异 < 6%**：99% 耗时是 LLM 调用，框架本身开销忽略不计，**别拿耗时当卖点**
- ⚠️ **简单 demo 看不出真正差异**：真正的差异在 **"加新需求时改动量"**（见 Q3）

---

## 🤔 关卡 3 分析题

### Q1. 两框架最终答案是否一致？意味着什么？

**v1**：一致，都答对了"上海更热 / 温差 5°C / 3 倍 = 15°C"，仅措辞不同（来自 LLM 输出随机性）

**修订**：一致。意味着两版做了**等价的工作**，对比是公平的。如果框架影响了答案，那叫"框架污染"，对比就没意义。这是任何对比实验的前提验证 —— 类似 ML 里"先确认两个模型在 baseline 数据上同分布"。

---

### Q2. 暴露内部状态的成本差异，对应什么设计哲学？

**v1**：langgraph 更开放和透明，HelloAgents 更封装隐藏。

**Review**：表层描述对了，没用到提示词汇 → 没答到**范式层**。

**修订 — 核心范式区别：State 作为一等公民 vs 副作用**：

- **HelloAgents 风格 = 命令式**：state 是过程的**副作用**，藏在 `self.messages` / `self.iteration` 里。要拿数据必须主动暴露（改 `self.messages` 那一步就是"打破封装"），调试是**黑盒**
- **LangGraph 风格 = 声明式**：state 是**一等公民（first-class citizen）**，输入输出都是显式 dict，节点是"读 state → 写 state"的纯函数。`result["messages"]` / `result["iteration"]` 天生可访问，调试是**白盒**

→ 跟 React `useState`、Redux "single source of truth"、函数式编程 "data over behavior" 是**同一种哲学**：**用数据结构表达控制流**，比用控制流操纵数据结构更可观测、可测试、可持久化。

---

### Q3. 加"重启恢复对话"分别要改多少行？

**LangGraph 版** ≈ **3 行**（Day 12 实测过）：
1. `from langgraph.checkpoint.sqlite import SqliteSaver`
2. `with SqliteSaver.from_conn_string(...) as cp:`
3. 编译时多传一个参 `graph.compile(checkpointer=cp)` + 调用时加 `config={"configurable": {"thread_id": ...}}`

**业务代码 0 行改动**，节点函数签名都不变。

**MiniReActAgent 版** ≈ **15-25 行 + 5 个新坑**：
1. 加 `thread_id` 参数到 `__init__` （+1 行）
2. `run()` 开头：`messages = load_from_file(thread_id)` 不存在则初始化（+5 行）
3. `run()` 结尾：`save_to_file(thread_id, self.messages)`（+3 行）
4. 处理"二次进入时不要再加 system prompt"（+3 行，注意：这就是 Day 12 关卡 2 踩过的 reducer 重复坑）
5. thread_id → filename 安全映射（避免路径注入）（+3 行）
6. 并发安全（多进程同时写同 thread）→ 加文件锁（+5 行，否则就是 race condition bug）

**还得自己想清楚 5 个新问题**：
- 文件 vs SQLite 怎么选
- 序列化格式 (json / pickle)
- 历史压缩策略（messages 无限增长怎么办）
- 加密（生产场景对话内容敏感）
- 错误恢复（写了一半进程被杀，文件半残）

→ **这就是 Day 14 博客最有冲击力的论点**：
> **"3 行 vs 25 行 + 5 个坑"**——LangGraph 不是省了 22 行代码，而是省了**22 行代码 + 5 个生产事故 + 一个团队季度**。

这才是工程框架的真正价值：**把分布式系统里"没人想第二次踩"的坑，做成默认行为**。

---

## 🎓 Day 13 总复盘

### 3 个核心收获

1. **简单场景两框架等价，差异在"扩展时刻"才现身**
   - demo 阶段：83 行 vs 73 行，46s vs 49s，答案一致，看似"何必学 LangGraph"
   - 加持久化：3 行 vs 25 行 + 5 个坑 → 这才是分水岭
   - **教训**：选框架不看 hello world，看 "加第三个需求时谁还能优雅"

2. **State 一等公民 = 可观测性的基石**
   - LangGraph 拿 metrics 0 成本（result 字典里全有）
   - HelloAgents 拿 metrics 必须改源码暴露 self.messages
   - 同样的"可观测性"，两版的代价差了一个数量级
   - **这是声明式范式相对命令式的核心价值**：把状态从过程中解放出来

3. **工程框架的真正价值不是"省代码"，是"省踩坑"**
   - LangGraph checkpointer 替你处理：序列化、原子写、并发、thread 隔离、time travel、HITL ...
   - 自己写一遍，每一项都是一次生产事故
   - **类比**：用 SQLAlchemy vs 自己写 SQL —— 不是为了少打字，是为了别在 SQL 注入上栽跟头

### Day 14 博客提纲（草稿）

**标题**：《写完同一个 Agent 两遍后，我才懂 LangGraph 在卷什么》

1. **导语**：用 80 行手写 vs 用 LangGraph，答案一样，那为什么选 LangGraph？
2. **数据先行**：贴对比表（3 行 vs 25 行 + 5 个坑）
3. **范式之战**：state-as-first-class-citizen 是怎么改变游戏规则的（Q2 答案精炼版）
4. **真正的拐点**：5 个生产场景（调试/A-B/HITL/灾备/教学）每个都吃 checkpointer 红利
5. **结语**：什么时候不该用 LangGraph？（提示：纯 demo / 一次性脚本 / 团队还没准备好理解 reducer）

### 给未来自己的提醒

- 写"对比"类内容时，**先验证 baseline 等价**（Q1），否则结论站不住
- 别拿耗时当卖点（99% 是 LLM 调用，看不出框架差）
- 真正的卖点是 **"扩展性差异 = 业务速度差异"**，这是面试官 / 老板能听懂的话术

### 面试 4 句话备答

- "选框架不看 hello world，看加新需求时改动量"
- "LangGraph 把 state 升级成一等公民，这是它能做 time travel 和 HITL 的根本"
- "checkpointer 是 3 行业务代码 + 5 个工程难题的组合优惠"
- "命令式/声明式 = 黑盒/白盒 = 调试基本靠 print / 调试可时间旅行"

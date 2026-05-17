# Day 12：LangGraph 进阶 — Checkpointer 持久化 + Time Travel

> **日期**：2026-05-17
> **进度**：关卡 1 / 2 / 3 ✅ 全部通过
> **依赖**：Day 11 关卡 3（已通过）的 `langgraph_hello.py` 直接复用 graph/state/nodes

---

## 🎯 今日地图

```
关卡 1: MemorySaver           ──→  thread_id 内存级跨 invoke
   │
   ↓
关卡 2: SqliteSaver           ──→  落盘，重启进程能恢复
   │
   ↓
关卡 3: Time Travel           ──→  get_state_history + checkpoint_id 分叉重跑
```

---

## 📚 新概念速记

### thread_id
- 一个独立的"会话"标识符（字符串，你自己起）
- 同一 thread 内的多次 `invoke` 共享 state
- 不同 thread 完全隔离
- 类比：浏览器的不同 tab，每个 tab 独立 cookie / session

### checkpoint_id
- thread 内每一步的快照 ID（每次节点执行后框架自动写入）
- 由框架生成（UUID 风格）
- 可以用来"回到过去某一步"

### config 字典
```python
config = {
    "configurable": {
        "thread_id": "user-001",         # 必传：决定加载哪个 thread 的 state
        "checkpoint_id": "abc-123",      # 可选：从指定历史点回放/分叉
    }
}
app.invoke(state_or_None, config)
```

| 配置 | 行为 |
|---|---|
| 只给 `thread_id` | 从该 thread 最新 checkpoint 继续 |
| 给 `thread_id` + `checkpoint_id` | 从指定历史点回放，新的执行会形成分叉 |

---

## ✅ 关卡 1 成果（MemorySaver）

**实现**：`build_graph_with_checkpointer(checkpointer)` 接受任意 saver（不绑定 Memory）

**测试**：同一 thread_id="user-001" 两次 invoke
- 第 1 次：完整初始 state（system + user "北京今天温度"）→ messages = 5
- 第 2 次：只传 `{"messages": [{"role":"user", "content":"上海呢"}]}` → messages = 9

**核心证据**：第 2 次 LLM 输出 *"上海今天的温度是15°C，比北京高5°C"* —— 凭借 checkpointer 自动加载的历史 messages 推断出"温度"语境。Day 11 没记忆版本永远做不到。

---

## ✅ 关卡 2 成果（SqliteSaver）

**实现**：`SqliteSaver.from_conn_string(".day12_checkpoints.db")` 是 context manager，必须 `with` 包裹。

**实验设计**：用 sys.argv 区分子命令，模拟两个独立 Python 进程：
```bash
python langgraph_checkpoint.py 2a  # 进程 A：thread_id="user-002" 问北京
# 进程退出
python langgraph_checkpoint.py 2b  # 进程 B：同 thread_id 接着问"那上海呢"
```

**核心证据**：进程 B 启动时内存里没有任何上次的对象，但 messages 仍能累加到 9 条 → **state 通过 SQLite 文件跨进程传递**。

**接口同形性**：换 saver、build_graph 函数、test 函数本体几乎不动 —— 这是策略模式的实战体现。

---

## ✅ 关卡 3 成果（Time Travel）

**实现**：`graph.get_state_history(config)` 列出 thread 内所有 checkpoint，按"新到旧"返回。每个 `StateSnapshot` 含 `.config` / `.values` / `.next` / `.metadata` / `.parent_config`。

**分叉逻辑**：
1. 找出 `next == ("llm",)` 且最后一条是 Observation 的 cp（即"工具刚返回、即将进 llm"）
2. `graph.invoke(None, config_fork)` —— input=None 让框架完全用快照里的 state
3. 框架从该 cp 派生新 cp 串，原线时间线保留

**实测数据**：
- thread "user-002" 共 8 个历史 cp
- 选 cp[4]（messages=4 时刻）分叉重跑
- 分叉后该 thread 历史变成 10 个 cp（原 8 + 新 2）
- 分叉得到的 final_answer 与原线一致（说明 LLM 这次输出稳定）

**关键观察**：
- `next` 字段的语义是"**接下来要跑哪个节点**"，不是"已经跑完了什么"。这就是为什么从 `next=("llm",)` 的 cp 能"重跑 llm"
- `cp_id` 前 8 位 `1f151d94` vs `1f151d98` 不同，说明它们属于**两次不同的 invoke 会话**（part1 和 part2），但都在同一个 thread 下

---

## 🛠️ 工程改进点

跟 Day 11 比新增了 2 个细节：

1. **CLI 子命令**：用 `sys.argv` 把 4 个测试函数做成可独立调用的子命令（`1` / `2a` / `2b` / `3`），不用每次注释切换。这是 Python 工程脚本的标准做法
2. **system_prompt 模块级常量**：把 `SYSTEM_PROMPT.format(tools_desc=...)` 提到模块顶层一次性算好，避免每次 invoke 重复格式化（也修了 Day 11 遗留的 `{tools_desc}` 没替换的 bug）

---

## 🐛 踩坑

### 坑 1：reducer 不区分"初始化"和"追加"，重跑会污染 state

**现象**：同一个 thread_id 第二次跑 `invoke({"messages": [system, user, ...]})`，messages 里会多出一份重复的 system + user。

**根因**：`Annotated[list, operator.add]` reducer 永远是"追加"语义。框架不知道你这次传的是"覆盖初始化"还是"追加新消息"，统统 append。
- 第 1 次 invoke：DB 空 → 追加 → `[sys, user]` 开始正常 ReAct
- 第 2 次 invoke 同 thread_id：DB 已有 5 条 → 又追加 `[sys, user]` → 中间出现重复的 sys + user

**长期记忆 / 设计原则**：
- **一个 thread_id 对应一次对话生命周期**
- 新对话 → 新 thread_id（用 uuid 等）
- 延续对话 → 同 thread_id，**只传新增的 user 消息**，不要再传 system
- 想"重启对话"→ 清 DB 或换 thread_id，不要在同一个 thread 上覆盖

**3 种修复方案**：
1. 测试时每次清 DB（最简单）
2. 每次用新 thread_id（生产场景）
3. invoke 前 `graph.get_state(config)` 检查是否有历史，有就跳过初始化（最优雅）

---

## 📝 4 题对比题（含 Cascade Review 修订版）

### Q1. thread_id 角色 + 为什么不自动生成

**v1**：扮演唯一会话的标识符，让用户可以控制多个独立的会话。

**Review**：是什么答对了，"为什么不自动生成"没答到。

**修订**：
- **角色**：唯一会话标识 → 决定从哪个 thread 加载历史 state、新写的 cp 归属哪个 thread
- **为什么必须用户传**：
  1. **跨进程语义**：自动生成的 ID 进程退就丢，下次没法关联。用户传 = 应用层有责任把它持久化到业务库（user_id / conversation_id）
  2. **业务语义对齐**：thread_id 通常 = 业务上的"会话 ID"，强制传 = 强制思考"这次 invoke 属于哪个业务实体"
  3. **避免隐式状态**：自动生成会让"同一 graph 跑两次到底是 1 个 thread 还是 2 个" 语义模糊，强制传 = 永远显式

→ 一句话：**框架不知道你的业务边界在哪儿，必须由你声明**。

---

### Q2. MemorySaver / SqliteSaver 设计范式

**v1**：依赖注入

**Review**：部分对，但不是最准的命中。DI 是"怎么给"，没回答"为什么能换"。

**修订**：**策略模式（Strategy Pattern）+ 依赖倒置（DIP）+ 依赖注入（DI）三件套**

- **策略模式**：同一抽象 `BaseCheckpointSaver`，多个可互换实现（Memory / Sqlite / Postgres / Redis）
- **里氏替换 + 依赖倒置**：graph 依赖抽象接口而不是具体类
- **依赖注入**：把"用哪个 Saver"的决策从 graph 里抽出去，由调用方注入

→ 严谨答案：**"基于策略模式的依赖注入，体现了依赖倒置原则"**。

---

### Q3. checkpoint_id 分叉 vs Git；做调试工具怎么用

**v1**：commit↔checkpoint，branch↔分叉。可以对比不同输入/参数，或修复错误路径。

**Review**：类比对，但应用太薄。

**修订 — Git ↔ LangGraph 精确映射**：

| Git | LangGraph |
|---|---|
| commit | checkpoint |
| SHA | checkpoint_id |
| branch | thread_id |
| HEAD | thread 当前最新 cp |
| `git log` | `get_state_history` |
| `git checkout <sha>` | `invoke(None, {cp_id})` |
| `git checkout -b new` | 从老 cp 用新 thread 重跑 |
| `git stash` | interrupt + resume |
| `git revert` | 从更早 cp 重新走 |
| `git bisect` | cp 间二分找 bug |

**核心不同**：
- Git 你**手动 commit**；LangGraph **每个节点跑完自动 commit**
- Git 是文件系统快照；LangGraph 是 state 结构快照（dict 序列化）

**做调试工具会怎么用 — 5 个具体功能**：

1. **错误回放复现**：异常时定位到出错前 cp，一键重跑该步（无需重跑前 N-1 步）
2. **步进调试器**（Agent 版 GDB）：`compile(interrupt_after=["llm","tool"])` 让每节点自动停；UI 提供 Step Over / Step Back / Run；左面板 state diff
3. **A/B Prompt 实验台**：从同一 cp 用不同 thread_id 跑出多个分支，并排对比效果
4. **HITL 人工介入**：高风险动作前 interrupt，审批人编辑 state 后 resume；杜绝 LLM 直接造成生产事故
5. **教学回放**：把精彩解题过程做成"录像"，时间轴拖动看 state 变化、可在任意点分叉自己试

→ 一句话：**LangGraph checkpointer 让 Agent 调试从"黑盒重跑碰运气"变成"白盒时间旅行"，是它对比其它框架最硬核的差异化能力**。

---

### Q4. state 塞 OpenAI client 会怎样

**v1**：会报错，节点不应在 state 里存不可序列化对象。

**Review**：结论对，缺"那应该放哪儿"的指导。

**修订**：
- **会怎样**：报错（pickle 不了 socket / SSL context / file handle）。即使没报错，跨进程恢复时 client 也是无效对象（连接已断）
- **正确做法 = "纯数据 vs 计算资源"二分**：
  - **State**：纯数据 = 输入输出 / 中间结果（messages、iteration、tool_outputs、scratchpad）
  - **节点函数闭包 / 模块级常量**：计算资源 = LLM client、HTTP session、DB connection、向量库 client
- **节点设计提示**：
  - LLM client 在文件顶层 `LLM = OpenAI(...)`，节点直接引用全局名
  - 节点是"无状态计算单元"——只读 state、写 state，不"持有"任何东西
  - 这样换实现（OpenAI → Anthropic）只改顶层 1 行，节点不动

→ 一句话：**state 是数据快照，client 是工具箱，两者必须分家**。

---

## 🎓 Day 12 总复盘

**3 个核心收获**：

1. **持久化 = state + thread_id + checkpointer 三位一体**
   - state 是"内容"，thread_id 是"边界"，checkpointer 是"存储引擎"
   - 三者解耦让"换存储"零代码改动 —— Memory / Sqlite / Postgres / Redis 共用一套 graph 代码
   - 这是工程上能横向扩展的根本（Day 11 学的"数据/计算/控制流解耦"在持久化这层再次体现）

2. **Time Travel = 把 Git 的演化模型搬到 Agent state 上**
   - 框架"每节点跑完自动 commit"是关键创新（Git 要手动）
   - `next` 字段告诉你"下一步要跑谁"，让"重跑某节点"语义清晰
   - 真实价值不在"好玩"，而在 **5 个生产级场景**（调试 / 步进 / A/B / HITL / 录像），每个都对应一种产品需求

3. **reducer 是双刃剑**
   - 让节点"只关心增量"是声明式的精髓
   - 但**永远是追加语义**，导致重复 invoke 同一个初始 state 会污染历史
   - 长期记忆：**一个 thread_id = 一次对话生命周期**，新对话用新 ID，延续对话只传增量

**给未来自己的提醒**：
- 写 invoke 前先问 "我要用旧 thread 还是新 thread"，不要在同一个 thread 反复初始化（坑 1 教训）
- state 字段拼写错框架不报错（Day 11 学的），加上 checkpointer 后这种 bug 会被持久化进 DB 更难发现
- 永远不要把 client / connection / 任何 stateful 对象塞进 state（Q4）

**面试预备**：4 句话能流畅说出
- "thread_id 是业务边界声明，必须用户传"
- "Memory/Sqlite Saver 是策略模式 + DIP，换存储零代码改动"
- "checkpoint 是 Git 模型在 Agent state 上的应用，差异是自动 commit"
- "state 存数据，client 存模块顶层常量，两者绝不混"

---

## 📌 遗留问题（不阻塞 Day 13）

1. `requirements.txt` gitignored，新机器跑 setup.sh 不会自动带上 `langgraph-checkpoint-sqlite` —— 这是项目原有问题
2. `system_prompt` 现在是模块级常量，跟 Day 11 不一致；下次重构 `langgraph_hello.py` 时也应该统一

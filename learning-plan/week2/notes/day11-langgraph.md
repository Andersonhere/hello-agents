# Day 11：LangGraph 入门

> **日期**：2026-05-12
> **进度**：关卡 1（线性 graph）✅ 已完成
> **下一步**：关卡 2（加 LLM 节点）+ 关卡 3（条件边 + 循环）

---

## 🎯 关卡 1 成果

```
关卡 1 输出: {'msg': 'say: hello world'}
✅ 关卡 1 通过
```

代码 → `code/week2/langgraph_hello.py`

---

## 📚 LangGraph 4 个核心概念

```
       State (TypedDict / Pydantic)
         ↑ 节点读取 / 写入
         │
   [Node A] ──Edge──► [Node B] ──Conditional──► [Node C]
                                     │
                                     └──► [Node D]
```

| 概念 | 类比 Day 10 | 一句话本质 |
|------|-------------|-----------|
| **State** | `messages` 局部变量 | 节点之间传递的数据快照，**TypedDict 强约束 schema** |
| **Node** | `run()` 里的某一步 | 一个**纯函数** `(state) -> {字段更新}`，返回的 dict 会 merge 到 state |
| **Edge** | `for` 循环里的下一步 | **静态跳转**：执行完 A 必去 B |
| **Conditional Edge** | `if action[0]=="finish": break` | **动态跳转**：根据 state 返回"下一节点名" |

---

## 💡 Q1/Q2/Q3 写之前的预测题

### Q1. State 和 Day 10 的 messages 有什么区别？

**A1（修订版）**：
- 浅层：State 抽象，messages 具体
- **深层**：State 是**强类型 schema 约束**、显式可观测；messages 是局部变量、隐式不可控
- **价值**：State 让节点解耦——任何节点只关心 schema 里的字段，不需要知道前面节点是谁。这是 LangGraph 能做**持久化（checkpointer）和可视化**的根本原因。messages 局部变量做不到。

### Q2. 节点函数 return 一个 dict，框架怎么处理？

**A2**：**merge**（不是 replace）。
- 节点 `return {'msg': '新值'}` 会被框架用作"变更指令"，去 merge 到现有 state
- 如果字段是 `list` 且想累加而非覆盖，要用 `Annotated[list, operator.add]`（关卡 2 会碰到）

### Q3. conditional_edge 返回的是什么？

**A3**：**下一节点的名字字符串**（也可以是 `END` 常量）。
- 函数签名：`def route(state) -> Literal["node_a", "node_b", END]`
- 框架根据返回值跳转

---

## 🐛 关卡 1 踩坑记录

### 坑 1：venv 没激活，ModuleNotFoundError

```bash
# ❌ 直接 python3 用的是系统解释器
python3 langgraph_hello.py
# → ModuleNotFoundError: No module named 'langgraph'

# ✅ 先激活 venv
source learning-plan/workspace/venv/bin/activate
python3 langgraph_hello.py

# ✅ 或一行不激活
learning-plan/workspace/venv/bin/python3 langgraph_hello.py
```

**长期记忆**：
- 每个项目独立 venv
- 每次新开终端都要激活
- `pip install` 之前确认 prompt 前有 `(venv)`
- IDE 解释器要选对

### 坑 2：`graph.msg.add_node` ❌

`graph` 是 `StateGraph` 实例，`add_node` 是它的方法，**不通过 state 字段访问**。`msg` 是 State schema 里的字段名，跟 graph 没关系。

```python
# ❌ 错
graph.msg.add_node('hello', hello_node)

# ✅ 对
graph.add_node('hello', hello_node)
```

### 坑 3：纯函数 vs 修改 state（⭐⭐⭐ 重磅设计哲学 / 面试必考）

第一版我写的：

```python
def hello_node(state):
    state['msg'] += 'hello'        # 直接改入参 state
    return {'msg': state['msg']}
```

虽然这版能跑通关卡 1，但**违反 LangGraph 核心设计**，会引发 5 个严重问题。

#### 一句话本质

> **LangGraph 把 state 当"不可变快照"管理。你直接改它 = 破坏框架的核心机制。**
> **节点是函数，不是脚本。** 函数的入参是只读的，你只能 return 新值，不能改入参。

#### 5 个具体问题（按严重性排序）

##### 问题 1：Checkpoint 持久化数据被污染（最严重）

LangGraph 的招牌特性是 **checkpointer**——每一步 state 存到 SQLite/Redis/Postgres，断电后能从任意一步恢复。框架内部大致流程：

```python
checkpoint_before = deepcopy(state)         # 进入节点前快照
result = node(state)                         # 执行你的节点
checkpoint_after = merge(state, result)     # 应用变更
save(checkpoint_before, checkpoint_after)   # 存两份
```

如果你直接 `state['msg'] += 'hello'`：

- `checkpoint_before` 已经被你**当场污染**
- 存进数据库的"前快照"和"后快照"看起来一样
- **从这个节点回放永远得不到正确结果**

##### 问题 2：时间旅行（Time Travel）失效

LangGraph 支持"回到第 3 步重新跑"——前提是每一步 state 都是独立快照。
你直接改 state 后，第 3 步的 state 和第 4 步指向同一个对象，"回到第 3 步"取到的是**已被第 4 步污染的 state**，不是当时的快照。

##### 问题 3：并发节点踩踏

LangGraph 1.x 支持**并发节点**（一个节点同时分发到两个下游）：

```python
graph.add_edge("split", "branch_a")
graph.add_edge("split", "branch_b")
# branch_a / branch_b 并发执行，都拿同一个 state
```

如果两个节点都直接改 `state['msg']` → **数据竞争（race condition）**，一个节点的修改被另一个覆盖，结果不确定。

而 return dict 模式下，框架知道两边的"变更指令"，可以用 reducer（如 `operator.add`）合并成一个确定结果。

##### 问题 4：类型校验/序列化失败

直接改 state 时如果不小心拼错字段名（如 `state['msgg'] = ...`），框架**完全不知道**，等下游节点读不到数据才炸——极难调试。
而 return dict 时框架会用 State schema 校验返回的字段。

##### 问题 5：违反节点的"纯函数"契约

LangGraph 文档明确：节点应该是 **pure function**——同样输入永远产生同样输出、无副作用。

| 风格 | 代码 | 副作用 |
|------|------|--------|
| ❌ 不纯 | `state['msg'] += ' hello'; return {...}` | 修改了入参 state |
| ✅ 纯 | `return {'msg': state['msg'] + ' hello'}` | 只读 state，返回新值 |

纯函数的好处：

- 单元测试不需要 mock 框架
- 同一个节点可以在多个 graph 复用
- 工具链可以静态分析（画图、生成文档）

#### 实测验证：外部 dict 也会被污染

```python
def bad_node(state):
    state['msg'] += ' BAD'         # 改了 state
    return {'msg': state['msg']}

initial = {"msg": "start"}
app.invoke(initial)
print(initial)   # {'msg': 'start BAD'}  ← 你的初始字典被污染了！
```

→ 这是**最难排查的 bug**：调用者根本不知道自己传进去的 dict 会被改。

#### 关于 return dict 的 merge 行为

```python
class S(TypedDict):
    msg: str
    count: int

def node1(state):
    return {'msg': 'hi'}    # 只更新 msg

# state 进来 = {'msg': 'start', 'count': 5}
# 节点执行后    = {'msg': 'hi',    'count': 5}   ← count 没动 ✅
```

**return dict 里没出现的字段会保留原值**，所以叫 merge。
对于 `list` 字段想累加而非覆盖，要用 `Annotated[list, operator.add]`（关卡 2 会碰到）。

### 坑 4：字符串拼接缺空格

```python
state['msg'] += 'hello'   # 输出 "say:helloworld"
state['msg'] += ' hello'  # 输出 "say: hello world" ✅
```

---

## 🔄 Day 10 → LangGraph 思维转换

| Day 10 命令式 | LangGraph 声明式 |
|------|------|
| `messages = []` | `class State(TypedDict): messages: list` |
| `messages.append(x)` | 节点 `return {"messages": [x]}`（auto merge） |
| `response = llm.create(...)` | 写一个 `call_llm(state)` 节点 |
| `if action.startswith("Finish"): break` | `conditional_edge` 返回 `END` |
| `while True: ...` | 用环形边 `add_edge("call_tool", "call_llm")` |

**核心转变**：
- 命令式：你写"先做什么再做什么"
- 声明式：你画"图长什么样"，框架帮你跑

---

## 🚀 接下来：关卡 2 + 关卡 3

### 关卡 2 目标

加一个 LLM 节点：
```python
class LLMState(TypedDict):
    question: str
    answer: str

def ask_llm_node(state) -> dict:
    # 读 state["question"]，调 LLM，返回 {"answer": ...}
```

预期收获：体验"节点级别的关注点分离"——这个节点只管"问 LLM"，不关心后续怎么处理答案。

### 关卡 3 目标

用 LangGraph 重写 Day 10 的 ReAct：
- 节点 1：`call_llm`
- 节点 2：`call_tool`
- 条件边：根据 LLM 输出判断去 `call_tool` 还是 `END`
- 环形：`call_tool` → `call_llm`（继续推理）

预期收获：**对比 Day 10 的 80 行 vs LangGraph 的多少行 + 调试体验差距**。

---

## 📝 关卡 1 完成的对比题（关卡 3 后再补全）

### Q1. LangGraph State vs 我手写 messages 的痛点？
**A**：LangGraph 强制定义 schema → 节点解耦 + 可序列化 + 可视化；手写 messages 是局部变量 → 节点强耦合 + 改一处全要改 + 没法持久化。

### Q2. 节点函数签名 `(state) -> dict` 复用性如何？
**A**：（关卡 2 后回答）

### Q3. conditional_edge vs if-else 调试方便程度？
**A**：（关卡 3 后回答）

### Q4. LangGraph 重写 ReAct 会少多少代码？
**A**：（关卡 3 后回答）

# Day 11：LangGraph 入门

> **日期**：2026-05-12 起 → 2026-05-17 完结
> **进度**：关卡 1 / 2 / 3 ✅ 全部通过
> **下一步**：Day 12（条件边进阶 + checkpointer 持久化）

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

## ✅ 关卡 2 / 3 成果

### 关卡 2（LLM 节点）
- 配置 scnet Qwen3-235B-A22B（OpenAI 兼容协议）
- 单节点 `ask_llm_node` 跑通 QA：`state["question"]` → LLM → `{"answer": ...}`
- **关键认知**：LLM client 在模块顶层初始化（连接复用），节点函数只做"组装请求 + 解析响应"

### 关卡 3（ReAct 重写）
- 4 个组件：`ReActState`（带 `Annotated[list, operator.add]` reducer）/ `call_llm_node` / `call_tool_node` / `should_continue`
- 图结构：`START → llm → [tool↔llm 循环 / END]`
- **跑通输出**：1 轮迭代解决"北京温度×2"问题，5 条 messages
- **真实代码量对比**：Day 10 ~80 行手写循环 vs Day 11 ~50 行节点+图（节点 40 + 路由 8 + build 7）

---

## 🐛 关卡 3 踩坑（⭐⭐⭐ 调试肌肉记忆）

### 坑 5：`self.xxx` 写在模块级函数里
从 Day 10 类方法的肌肉记忆复制过来，`call_llm_node` 不是方法没有 `self` → `NameError`。
**长期记忆**：LangGraph 节点是 **模块级纯函数**，client/model 在文件顶层初始化，节点直接引用全局名。

### 坑 6：消息是 dict 不是对象
```python
last_message.content      # ❌ AttributeError
last_message["content"]   # ✅
```
节点之间通过 dict 传递消息（OpenAI chat completions 格式），不是对象。

### 坑 7：`_parse_action` 返回 tuple 不是 dict
```python
action["tool_name"]   # ❌ TypeError: tuple indices must be integers
tool_name, params = action   # ✅ 解构
```
**教训**：用 unfamiliar 函数前先看签名，不要凭直觉假设返回类型。

### 坑 8：`fn(*tool_args)` 解包字符串
`tool_args` 是字符串 `"北京"`，`*` 解包 = 拆成单字符 `("北","京")` → `fn("北","京")` 报"2 个位置参数"。
**长期记忆**：
- `fn(x)` 单值传参
- `fn(*list)` 拆位置参数（list/tuple）
- `fn(**dict)` 拆关键字参数（dict）

### 坑 9：`final_answer` 塞整段 LLM 输出
原始写法 `final_answer = response.content` 把 `"Thought:...\nAction: Finish[20°C]"` 整段塞进去。
**正确做法**：用 `re.search(r"Finish\[(.*?)\]", content, re.DOTALL)` 提取方括号内容。
**教训**：字段语义要严格，"含 20" 测试虽过但答案污染了。

---

## 📝 4 道对比题（关卡 3 后回答，含 Cascade Review）

### Q1. State vs Day 10 messages 局部变量

**我的答案（v1）**：state 黑盒难理解；局部变量直观但复用差。

**Review**：错了一半。**State 恰恰是显式 schema、可观测、可序列化的**，是 LangGraph 能做 checkpointer / time-travel / 可视化的根本。局部变量才是真黑盒（藏在函数里，外部看不见）。

**修订答案**：
- State：TypedDict 强类型 + reducer 显式合并 + 节点间解耦 → 框架能拿来做持久化和并发安全合并
- 局部 messages：藏在 `run()` 内，每加一步都要改函数体，无法被外部观察 / 回放 / 暂停

### Q2. 节点函数 `(state) -> dict` 复用性 vs `run()` 方法

**我的答案（v1）**：复用性更好，因为可以被多个节点调用。

**Review**：循环论证。节点本身就是函数，"被节点调用"等于没说。

**修订答案**：
- 节点是**纯函数 + 固定契约**（入 state、出 partial state dict）→ 同一节点可放进不同 graph 复用；单测只需传 state dict，不用 mock 整个 Agent 类
- Day 10 的 `run()` 是 `MiniReActAgent` 实例方法，跟类强绑定 → 想单独测"调 LLM 这一步"必须 mock 整个对象

### Q3. conditional_edge vs if-else 调试方便程度

**我的答案（v1）**：conditional_edge 更方便，能清晰看到每条条件的执行路径。

**Review**：方向对但虚，没说出"为什么能看到"。

**修订答案**：conditional_edge 把路由逻辑从节点抽出来变成图上的边，框架可以：
- 自动 trace 每次跳转（配合 LangSmith 直接出时序图）
- 静态分析画出 graph 结构图
- 暂停/单步执行
而 if-else 散落在 `run()` 里只能 print log，没法被工具链识别。

### Q4. 重写代码量 + 复杂度

**我的答案（v1）**：会少很多代码，复杂度会降低。

**Review**：空洞无数据。手上明明有实测：

**修订答案**：
- 代码量：Day 10 mini_react_agent.py ~80 行 → Day 11 LangGraph 版 ~50 行，**减少 ~38%**
- 表面复杂度：降低（无 while + 无手写重试，框架接管）
- **真实认知复杂度：升高** —— 要学 5 个新概念（State / Node / Edge / Conditional Edge / Reducer）+ 1 套调用约定（return dict 触发 merge）
- 价值不在"少写"，在"**可扩展性**"——加 checkpointer 几行代码、加并发节点零额外代价，Day 10 手写版要重写一整轮

---

## 🎓 Day 11 总复盘

**3 个核心收获**：

1. **声明式 vs 命令式的思维切换**——从"我写流程"变成"我画图，框架跑流程"。一开始很别扭（关卡 3 写 4 个函数感觉支离破碎），但理解之后会发现：每个节点只关心自己输入输出，**节点间的调度交给图**，这是工程上能横向扩展的基础。

2. **纯函数节点是底线**——关卡 1 坑 3 的"直接改 state" 教训刻在心里：节点必须 `return dict` 不能改入参，否则 checkpointer/time-travel/并发都会炸。这是 LangGraph 5 个核心约束里最严格的一条，写代码时永远先问"我有没有 mutate state"。

3. **Reducer 是被低估的设计**——`Annotated[list, operator.add]` 看起来只是个累加器，实际上是 LangGraph 能做"并发节点安全合并"的关键。等关卡 3 之后看 LangGraph 的 `add_messages` 内置 reducer 实现，能体会到为什么 langchain 团队会把这套抽象当作核心。

**给未来自己的提醒**：
- 看 unfamiliar 函数前先看签名，**不要凭直觉假设返回 dict 还是 tuple**（坑 7）
- `*` / `**` 解包前先确认参数是字符串/列表/字典（坑 8）
- 字段语义要严格，**测试通过 ≠ 实现正确**（坑 9 的 final_answer 污染）

**面试预备**：Q1-Q4 修订答案是面试官最爱问的方向，下次能流畅说出"State 是 LangGraph 实现持久化/可视化的根基"、"节点纯函数让复用 + 单测变简单"、"conditional_edge 是工具链一等公民"、"代码量减少但认知复杂度升高，换来可扩展性"四句，本周博客就有素材了。

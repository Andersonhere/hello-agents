# Day 10：手写极简版 ReActAgent

> **日期**：2026-05-10
> **耗时**：约 3.5h（含 SSL 网络问题排查 0.5h）
> **产出**：`code/week2/mini_react_agent.py` 跑通"北京温度乘以 2"测试题

---

## 🎯 核心成果

- ✅ 不看官方源码独立实现 `MiniReActAgent`（约 80 行）
- ✅ 跑通三轮 ReAct 循环：`get_weather(北京) → 10°C → calculate(10*2) → 20 → Finish[20]`
- ✅ 实战工程必要项：3 次指数退避重试、`stop=["Observation:"]` 防 LLM 编造
- ✅ 用 `with_raw_response` 拿到完整 HTTP 响应，看清 token 消耗结构
- ✅ 发现 Qwen3 推理模型的 `reasoning_content` 字段特性

---

## 🔄 ReAct 循环本质

> **ReAct = SimpleAgent + 工具调用 + 思考-行动-观察循环**

最深刻的认知：**ReAct 不是魔法，是"prompt 约定 + 字符串解析 + while 循环"**。

具体做了什么：

1. **Prompt 约定**：告诉 LLM 输出格式必须是 `Thought: ... Action: 工具(参数)`
2. **字符串解析**：用正则从 LLM 输出里抠出 `tool_name` 和 `params`
3. **循环驱动**：执行工具拿到 Observation → 拼回 messages → 再问 LLM → 直到 `Finish[...]`

---

## 🧰 大模型是怎么"选择"工具的？

> 这是 Day 10 真正学到的最重要的事：**LLM 没有"选择能力"，它只是文本续写**。

### 一句话本质

**工具选择 = 文本续写 + Prompt 设计 + 字符串约定**

LLM 看到的是：

```text
你是一个会使用工具的智能助手。
可用工具：
- get_weather: 查询城市温度
- calculate: 计算数学表达式

输出格式：
Thought: ...
Action: 工具名(参数)
```

然后续写 `Thought: 我需要查温度。Action: get_weather(北京)`。

**它没有"决定调用 get_weather"——它只是续写出了这串字符**。
"调用"是**你的代码**做的：你正则提取，你查表，你执行函数。

### 选择的"机制"分三层

| 层 | 谁在做 | 怎么做 |
|----|--------|--------|
| **L1 文本续写** | LLM | 根据 prompt 中的工具描述，预测最合适的下一段文字（Thought + Action） |
| **L2 字符串解析** | 你的代码 | 正则提取 `Action: xxx(yyy)` |
| **L3 工具调度** | 你的代码 | 在 `TOOLS` 字典里查 xxx，执行 fn(yyy) |

### 影响 LLM "选对"工具的 4 个关键因素

| 因素 | 怎么做好 | 反例 |
|------|---------|------|
| **工具名要语义自解释** | `get_weather` ✅ | `tool_a`, `func1` ❌ |
| **工具描述要写清场景** | "查询城市温度，参数: city (字符串)" ✅ | "查天气" ❌ |
| **Few-shot 示例** | 给 1-2 个完整的 ReAct 链路示例 | 只描述格式不举例 ❌ |
| **训练数据覆盖** | 选 GPT-4 / Claude / Qwen3 等大厂 SOTA | 用未对齐过 function calling 的小模型 ❌ |

### 对比新世代：Function Calling 协议

OpenAI 2023 后推出了**结构化 tool_calls**，等于把上面 L1+L2 都内置进了 SDK：

```python
# 你的 ReAct（手动 prompt + 正则解析）
content: "Action: get_weather(北京)"  # 字符串
→ 你正则切

# Function Calling（SDK 直接给结构化对象）
tool_calls: [{ "function": { "name": "get_weather", "arguments": "{\"city\":\"北京\"}" } }]
→ 直接拿 .arguments
```

**本质相同**——都是 LLM 根据 prompt 续写，然后程序执行。区别只在于：

- ReAct：你自己设计 prompt 格式 + 自己解析（**灵活但脆弱**）
- Function Calling：模型训练时就内置了 JSON 格式的特殊 token（**鲁棒但被绑定到协议**）

→ Day 13 LangGraph 会用 Function Calling，到时候对比体感最深。

---

## 💰 ReAct 的 Token 成本陷阱

跑测试题"北京温度×2"实测：

| 轮次 | prompt_tokens | completion_tokens | total | 增量原因 |
|------|---------------|-------------------|-------|---------|
| 第 1 轮 | 264 | 103 | 367 | 初始 system + question |
| 第 2 轮 | 299 (+35) | 154 | 453 | 多了 assistant1 + observation1 |
| 第 3 轮 | 339 (+40) | 134 | 473 | 多了 assistant2 + observation2 |
| **累计** | **902** | **391** | **1293** | — |

**关键洞察**：

- prompt_tokens 每轮线性增长（每轮把历史全发一遍）
- 总成本是 **N²/2** 量级（10 轮的对话 ≈ 50 轮单轮的成本）
- completion 里包含 Qwen3 的 `reasoning_content`（思考过程），所以 100+ token

**优化方向**（Week 2-3 会学）：

1. **prompt cache**（OpenAI 1h 缓存重复 prompt 部分）
2. **状态压缩**（LangGraph checkpointer 只存关键状态）
3. **总结代替原文**（把前 N 轮压成一句"已查到北京 10°C"）

---

## 📦 Chat Completion Response 字段速查

### 三方共建的 schema

| 来源 | 字段 |
|------|------|
| **OpenAI 协议** | `id`, `object`, `created`, `model`, `choices`, `usage`, `system_fingerprint`, `service_tier` |
| **Qwen3 推理模型扩展** | `reasoning`, `reasoning_content` |
| **vLLM 推理引擎扩展** | `prompt_logprobs`, `prompt_token_ids`, `kv_transfer_params`, `stop_reason`, `token_ids` |

### `finish_reason` 信号灯

| 值 | 含义 | 处置 |
|---|------|------|
| `stop` | 自然结束 / 命中 stop_words | ✅ 正常 |
| `length` | 被 max_tokens 截断 | ⚠️ 内容不完整，加大上限 |
| `tool_calls` | 模型调工具（FC 模式） | 解析 tool_calls 字段 |
| `content_filter` | 触发审核 | ❌ 检查 prompt |

### Qwen3 的 `reasoning_content` 隐藏陷阱

实测 Qwen3 第 3 轮响应：

```json
"content": "\n\nAction: Finish[20]",
"reasoning_content": "好的，用户问的是..."
```

**意味着**：你的 `Thought:` 在 prompt 里要求 LLM 输出，但 Qwen3 在它训练后**已经把思考挪到了 reasoning_content 字段**，你的正则在 `content` 里找 `Thought:` 是抓不到完整思考的。

**但 Agent 仍能跑通**——因为 `Action:` 还在 `content` 里，足够驱动循环。

---

## 🐛 踩坑记录

### 坑 1：TOOLS 数据结构混淆

最初定义为 `dict[str, tuple]`，但用 `for tool in TOOLS: tool['name']` 当成 list[dict] 用。

- **报错**：`TypeError: string indices must be integers, not 'str'`
- **修复**：用 `TOOLS.items()` 解构，或直接 `TOOLS[tool_name]` 查表。

### 坑 2：SSL 网络抖动

3 天后重跑，scnet 端 `[SSL: UNEXPECTED_EOF_WHILE_READING]`。

- **修复**：加 3 次指数退避重试（实战验证了 Day 9 A3 中识别的"工程必要：错误处理与重试"）。

### 坑 3：LLM 自编 Observation

如果不加 `stop=["Observation:"]`，LLM 会一口气把整个 Thought/Action/Observation 都续写完，把假数据当真。

- **修复**：传 `stop` 参数让服务端在出现这个字符串时主动截停。

### 坑 4：`exit(1)` vs `raise`

第一版重试失败后 `exit(1)` 直接杀进程。

- **修正**：改 `raise`，让异常向上传播，给上层调用者兜底机会。

---

## 📝 完成后的 3 题复盘

### Q1. `_parse_action` 用什么策略？格式偏离会怎样？

**A1**：用 `re.search(r"Action:\s*(.+)")` 抓最后一个 Action 行，再用 `split("(")` / `split(")")` 切参数。

鲁棒性差：

- 中文括号 `（）` 抓不到
- LLM 写成 `Action: get_weather("北京")` 会带引号，需 strip
- LLM 多写一行 `Action:` 会取到错的那行

→ 生产环境应该用 Function Calling 替代正则。

### Q2. 跑测试时 LLM 有没有自己编 Observation？

**A2**：没有，因为加了 `stop=["Observation:"]`，服务端主动截停。
从日志看 `stop_reason: "Observation:"` 验证了这一点。

**对比**：如果不加 stop，LLM 会一次输出完整 `Thought:...Action:...Observation:...Thought:...Action: Finish[xx]`，循环失效。

### Q3. ReAct = SimpleAgent + ___ + ___

**A3**：ReAct = SimpleAgent + **工具循环（while + 解析 Action）** + **结构化 Prompt 协议（Thought/Action/Observation 三段式）**

---

## 🎁 Day 10 简历素材片段

> 不看源码手写 ReAct Agent（80 行），跑通"查天气→计算"两步骤工具调用任务。
> 通过 `with_raw_response` 分析 token 消耗，发现 ReAct 的 prompt_tokens **N² 增长陷阱**；
> 识别 Qwen3 推理模型的 `reasoning_content` 字段会"分流"思考内容，导致 ReAct 文本协议失真；
> 在网络抖动场景下补充 3 次指数退避重试和 `stop_words` 防护，提升健壮性。

---

## 🚀 下一步：Day 11 LangGraph 入门

预期对比点：

- ReAct 手写 vs LangGraph `create_react_agent` 行数对比
- Prompt 解析 vs Function Calling 协议对比
- 手动 messages 累加 vs StateGraph 状态管理对比
- 没有持久化 vs `checkpointer` 持久化对比

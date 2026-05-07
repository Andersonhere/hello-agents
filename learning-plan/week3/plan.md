# Week 3：MCP 协议 + 记忆 + RAG + Tracing

> **周期**：Day 15 - Day 21
> **主题**：构建生产级 Agent 必备的四件套
> **产出**：一个集成了 MCP、长期记忆、RAG、LangSmith Tracing 的综合 Agent（Week 4 项目的"原型"）

---

## 🎯 修订说明（v2）

- ✅ **新增 Tracing & 评估**（Day 20）—— 就业方向必备
- ✅ **MCP 增加"手写最小 server"** —— 比只用现成 server 更扎实
- ✅ **RAG 提升深度** —— 你确认会用到，所以 chunking + retriever 都要动手
- ✅ **Day 21 整合复盘** —— 把四件套合并成一个 Agent，作为 Week 4 项目的 baseline

---

## 📋 本周目标

| 目标 | 验收标准 |
|------|----------|
| 掌握 MCP 协议 | 能调通现成 server **且**手写一个最小 server（≥1 个工具） |
| 理解记忆系统 | 能说清短期/工作/长期记忆的实现方式，并实现长期记忆持久化 |
| 掌握 RAG 全流程 | 能独立完成"文档 → chunking → embedding → 检索 → 注入 prompt" |
| 掌握 Tracing | 能用 LangSmith 看 trace 并基于 trace 优化一处 prompt |
| 整合能力 | 把上述四件套合并为一个 Agent 并跑通 |

---

## 📅 每日计划

| 日期 | 主题 | 重点任务 |
|------|------|----------|
| Day 15 | MCP 协议原理 + 跑现成 server | 跑通 `code/chapter10/05_UseMCPToolInAgent.py`，搞清 client/server 通信 |
| Day 16 | **手写最小 MCP server** | Python `mcp` 包，实现 1-2 个工具（如 `read_file`、`get_time`） |
| Day 17 | 记忆系统 | 短期：消息窗口截断；长期：用 SQLite 或向量库存"用户偏好" |
| Day 18 | RAG 全流程（上） | 文档加载、chunking 策略对比（固定大小 vs 语义分块） |
| Day 19 | RAG 全流程（下） | ChromaDB + embedding + 把 retriever 包成 Agent 工具 |
| Day 20 | **LangSmith Tracing** | 接入 LangSmith → 跑 10 次 → 看 trace → 优化一处 prompt |
| Day 21 | **整合 + 周复盘** | 合并四件套为一个 Agent；写复盘博客 |

---

## 📚 核心知识点

### 1. MCP 协议要点

```
Agent ⇄ MCP Client ⇄(协议)⇄ MCP Server ⇄ 实际能力
                    ↑
              JSON-RPC over stdio/SSE
```

**面试常问**：
- MCP 解决了什么问题？（工具复用、跨语言、解耦）
- MCP vs Function Calling 区别？（MCP 是协议层，FC 是 LLM 能力层）
- 一个 MCP server 暴露什么？（tools、resources、prompts 三类）

### 2. 记忆系统三层

| 层级 | 生命周期 | 实现 | 存什么 |
|------|----------|------|--------|
| 短期记忆 | 当前对话 | messages 列表 + 窗口截断 | 最近 N 轮对话 |
| 工作记忆 | 当前任务 | LangGraph State | 当前任务上下文、中间结果 |
| 长期记忆 | 跨会话 | SQLite / 向量库 | 用户偏好、历史事实、知识 |

**实践重点**：长期记忆做一个**"用户偏好"小 demo**——记住用户喜欢的语言、风格，下次对话自动应用。

### 3. RAG 必懂概念

```
[索引阶段] 文档 → 加载 → 分块 → embedding → 向量库
                          ↑
                    chunk_size / overlap 是关键超参

[检索阶段] 问题 → embedding → top-k 相似检索 → rerank(可选) → 拼 prompt → LLM
```

**至少做一次对比实验**：
- 同一文档，`chunk_size=200` vs `chunk_size=800` 的检索质量差异
- 这是博客素材，也是面试素材

### 4. Tracing（详见前一轮对话解释）

**Day 20 必做**：
1. 注册 LangSmith（免费额度足够）
2. 给你的 Agent 加 3 行环境变量启用 tracing
3. 跑 10 个不同问题
4. 在 LangSmith UI 上找出 1 个"token 浪费/逻辑绕弯"的 case
5. 改 prompt 后再跑，对比改进

**这一步做完，简历上可以写**：
> 基于 LangSmith trace 分析定位 prompt 缺陷，优化后 ReAct 循环平均轮次从 X 降至 Y，token 消耗降低 Z%。

---

## 🛠️ 关键约束（基于你的环境）

| 需求 | 替代方案（仅需 LLM key） |
|------|------------------------|
| Embedding 模型 | 用大模型 provider 自带的 embedding API（多数都有），或本地 `sentence-transformers` |
| 向量库 | **ChromaDB**（本地、零配置、零成本） |
| MCP server 数据源 | 本地文件系统 / mock 数据 |
| Tracing 后端 | **LangSmith**（注册即用，仅需 API key） |
| 评估数据集 | 你自己手写 10 个 Q&A pair |

---

## ✅ 验收清单

### Day 15-16 MCP
- [ ] 跑通官方示例 `05_UseMCPToolInAgent.py`
- [ ] 能画出 MCP 通信时序图
- [ ] **手写一个最小 MCP server**（暴露 1-2 个工具）
- [ ] 把自己的 server 接入 Agent 并调用成功

### Day 17 记忆
- [ ] 实现短期记忆窗口截断（避免 context 爆炸）
- [ ] 实现长期记忆存"用户偏好"，跨会话生效

### Day 18-19 RAG
- [ ] 文档加载 + chunking（至少试 2 种 chunk_size）
- [ ] ChromaDB 持久化向量库
- [ ] 把 retriever 封装成 Agent 工具
- [ ] 至少 5 个测试问题验证检索质量

### Day 20 Tracing
- [ ] LangSmith 接入成功
- [ ] 看到完整 trace 树
- [ ] 找出 1 处优化点并改进

### Day 21 整合
- [ ] 一个 Agent 同时具备：MCP 工具 + 长期记忆 + RAG + Tracing
- [ ] 写**周复盘博客**（800 字，含 trace 截图）

---

## 📁 产出位置

```
learning-plan/output/code/week3/
├── mcp_server_minimal/        # 手写的 MCP server
├── memory_demo.py             # 记忆系统 demo
├── rag_pipeline.py            # RAG 全流程
├── tracing_demo.py            # LangSmith 接入示例
└── integrated_agent.py        # ⭐ Day 21 整合版（Week 4 baseline）

learning-plan/output/notes/
└── week3-summary.md           # 周复盘博客
```

---

## 🔗 资源

### 代码参考
- `code/chapter10/` MCP 系列示例
- `code/chapter8/01_MemoryTool_Basic_Operations.py`
- `code/chapter8/04_RAGTool_MarkItDown_Pipeline.py`

### 外部资源
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [ChromaDB 文档](https://docs.trychroma.com/)
- [LangSmith 文档](https://docs.smith.langchain.com/)

---

## 🎓 周回顾自测

合上电脑回答：

1. 一次 RAG 调用从输入到输出经过哪些步骤？哪几步可能出错？
2. 短期记忆"满了"应该怎么办？至少说出 3 种策略
3. MCP server 和直接写 Python 函数当 tool 相比，多了什么、少了什么？
4. 你在 LangSmith 上发现的那个优化点，**用 1 句话**讲清前因后果

---

*[返回总计划](../README.md)*

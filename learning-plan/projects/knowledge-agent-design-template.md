# 项目设计文档模板（Day 22 使用）

> 复制本文件到 `learning-plan/output/projects/knowledge-agent/DESIGN.md` 后填写
> **今天不许写代码，只许画图、定接口、想清楚**

---

## 1. 功能边界

### MVP 必做
- [ ] 接收用户问题，基于本地文档库回答（RAG）
- [ ] 支持上传文档（txt / md / pdf）
- [ ] 长期记忆：记住用户偏好（语言、风格等）
- [ ] 通过 MCP 工具读写本地文件
- [ ] HTTP API 对外提供服务
- [ ] 每次调用都有 LangSmith trace

### 明确不做（防 scope 蔓延）
- [ ] 不做前端界面（只用 curl/Postman）
- [ ] 不做用户认证（默认单用户）
- [ ] 不做多文档库切换（一个全局库）
- [ ] 不做流式输出（先做同步）
- [ ] 不做 reranker（baseline 用 top-k 直出）

---

## 2. 用户故事（3-5 条）

例：
- **作为开发者**，我想把团队 wiki 喂入 Agent，**以便**快速查询规范
- **作为...**，我想 ...，以便 ...

---

## 3. 架构图

> 用 Excalidraw / draw.io 画好后截图嵌入这里
> 至少包含：用户 → FastAPI → LangGraph → (RAG / MCP / Memory) → LLM

```
[占位 - 在此处嵌入架构图]
```

---

## 4. LangGraph 状态图

> 画出 Node 和 Edge

**State 定义**（TypedDict）：
```python
class AgentState(TypedDict):
    messages: list          # 对话历史
    user_id: str            # 用户标识（用于读取长期记忆）
    retrieved_docs: list    # 当轮检索到的文档
    tool_results: list      # 工具调用结果
    next_action: str        # router 决策
```

**节点列表**：
| 节点 | 输入 | 输出 | 职责 |
|------|------|------|------|
| `load_memory` | user_id | messages 注入偏好 | 加载长期记忆 |
| `agent` | state | next_action | LLM 决策（调工具 or 答） |
| `retriever` | query | retrieved_docs | RAG 检索 |
| `mcp_tool` | tool_call | tool_results | 调 MCP server |
| `respond` | state | final_answer | 生成最终回答 |

**边**：
- `START → load_memory → agent`
- `agent →(条件)→ retriever / mcp_tool / respond`
- `retriever → agent`
- `mcp_tool → agent`
- `respond → END`

---

## 5. 工具列表

| 工具名 | 类型 | 入参 | 出参 | 说明 |
|--------|------|------|------|------|
| `search_knowledge` | 内置 | query: str, k: int=3 | list[Document] | RAG 检索 |
| `read_file` | MCP | path: str | str | 读本地文件 |
| `write_file` | MCP | path: str, content: str | bool | 写本地文件 |
| `save_preference` | 内置 | key: str, value: str | bool | 保存用户偏好 |

---

## 6. 数据模型

```python
# Document
{
    "id": str,
    "content": str,
    "metadata": {"source": str, "chunk_id": int}
}

# Memory (长期记忆 - SQLite)
{
    "user_id": str,
    "key": str,            # 如 "language", "code_style"
    "value": str,
    "updated_at": datetime
}

# ChatRequest
{
    "user_id": str,
    "message": str,
    "session_id": str | None
}

# ChatResponse
{
    "answer": str,
    "sources": list[str],   # 引用的文档
    "trace_url": str        # LangSmith trace 链接
}
```

---

## 7. API 设计

### POST /chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u1","message":"什么是 ReAct?"}'
```

Response:
```json
{
  "answer": "ReAct 是...",
  "sources": ["doc1.md#chunk3"],
  "trace_url": "https://smith.langchain.com/..."
}
```

### POST /upload
上传文档到向量库。

### GET /memory/{user_id}
查看用户偏好。

### DELETE /memory/{user_id}/{key}
删除某条偏好。

---

## 8. 测试集（≥10 个）

| # | 问题 | 期望涉及的能力 | 期望关键词 |
|---|------|----------------|-----------|
| 1 | 我喜欢用中文回答，记住 | save_preference | "已记住" |
| 2 | 什么是 ReAct? | RAG | "Thought, Action, Observation" |
| 3 | 帮我把当前文档总结写到 summary.md | MCP write_file | "已写入" |
| 4 | 读 readme.md 的内容 | MCP read_file | 文件内容 |
| 5 | 上次我让你记住的偏好是什么? | load_memory | 之前存的值 |
| 6-10 | （自己补充）| | |

---

## 9. 风险与备选方案

| 风险 | 缓解方案 |
|------|----------|
| Embedding 检索不准 | chunk_size 调优 / 加 metadata 过滤 / Day 27 评估时迭代 |
| Context 过长 | 长期记忆只取 top-N 偏好，对话历史窗口截断 |
| LLM 工具调用格式错误 | 用 LangGraph `ToolNode` + 重试 |
| MCP server 崩溃 | try/except 包裹，降级为告知用户 |

---

## ✅ 完成标准

- [ ] 9 个章节齐全
- [ ] 至少 2 张图（架构图 + 状态图）
- [ ] 测试集 ≥ 10 个问题
- [ ] 给非技术朋友念一遍能听懂功能边界

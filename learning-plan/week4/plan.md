# Week 4：项目实战 — 本地知识库 Agent

> **周期**：Day 22 - Day 30
> **主题**：用 LangGraph + RAG + MCP + 长期记忆 + Tracing 构建一个**简历级**后端 Agent
> **产出**：GitHub 项目 + README + 演示视频 + 复盘博客

---

## 🎯 修订说明（v2）

- ✅ **项目从"智能旅行助手"改为"本地知识库 Agent"** —— 纯后端、零外部 API 依赖、契合你"在公司用 Agent 提效"的目标
- ✅ **Day 22 单独做设计文档** —— 不写代码，只画图和定接口
- ✅ **Day 27 评估专题** —— 跑测试集 + Tracing 优化
- ✅ **Day 29-30 简历包装** —— README、架构图、5 分钟视频

---

## 🎯 项目：本地知识库 Agent（"我的 AI 知识助手"）

### 项目定位

一个能**吃文档、记偏好、查工具、可追踪**的后端 Agent。可以喂入：
- 个人笔记 / 公司内部文档 / 技术书
- 通过 HTTP API 提问，得到基于文档的回答
- 记住你的偏好（如"回答用中文"、"代码用 Python"）
- 可以读写本地文件（通过 MCP server）
- 所有调用可在 LangSmith 追踪

### 为什么这个项目最适合你

| 你的需求 | 本项目对应 |
|---------|-----------|
| 就业（Agent 岗） | 覆盖 LangGraph + RAG + MCP + Tracing 全部关键词 |
| 公司提效 | 直接喂入公司文档即可用 |
| 只有 LLM key | 零外部 API 依赖（embedding 用 LLM 厂商的或本地） |
| 重视质量 | 包含设计文档、测试、评估、文档包装全流程 |

### 技术栈

```
LangGraph (状态机)
  ├─ ChromaDB (向量库)
  ├─ MCP Server (本地文件读写)
  ├─ SQLite (长期记忆 / 用户偏好)
  ├─ LangSmith (Tracing)
  └─ FastAPI (HTTP 接口)
```

---

## 📅 每日计划

| 天 | 主题 | 不写代码？ |
|----|------|-----------|
| **Day 22** | 设计文档（**不写代码**） | ✅ 只画图、定接口 |
| Day 23 | LangGraph 状态机骨架 + 基础对话 | |
| Day 24 | 接入 RAG retriever 工具 | |
| Day 25 | 接入 MCP server（本地文件读写） | |
| Day 26 | 长期记忆（用户偏好持久化） | |
| Day 27 | LangSmith Tracing + 评估测试集（**重点**） | |
| Day 28 | FastAPI HTTP 接口 + Postman 调通 | |
| Day 29 | README + 架构图 + 部署说明 | |
| Day 30 | 5 分钟讲解视频 + 复盘博客 + 提交 GitHub | |

---

## 📋 Day 22 设计文档要求（重要）

**今天不许写代码**。完成 `learning-plan/output/projects/knowledge-agent/DESIGN.md`，包含：

1. **功能边界**：MVP 做什么、不做什么（明确说"不做 X"）
2. **用户故事**：3-5 条 "作为 X，我想 Y，以便 Z"
3. **架构图**：模块划分（Excalidraw / draw.io 截图）
4. **状态图**：LangGraph 节点和边的图
5. **工具列表**：每个工具的名称、入参、出参、归属（内置 / MCP）
6. **数据模型**：Message、Memory、Document 的字段定义
7. **API 设计**：至少 3 个 HTTP endpoint（含 request/response 示例）
8. **测试集计划**：列出 ≥ 10 个测试问题（Day 27 用）
9. **风险与备选方案**：embedding 不准怎么办？长 context 怎么办？

模板在 `learning-plan/week4/project-design-template.md`。

---

## 🛠️ 关键技术选型说明

| 组件 | 选型 | 原因 |
|------|------|------|
| 状态机 | LangGraph | 工业标准，简历加分 |
| 向量库 | ChromaDB | 本地零配置 |
| Embedding | LLM 厂商 API 或 `BAAI/bge-small-zh` 本地 | 你只有 LLM key，二选一 |
| 长期记忆 | SQLite | 标准库自带，零依赖 |
| Tracing | LangSmith | 行业事实标准，简历关键词 |
| HTTP 框架 | FastAPI | Python Agent 后端事实标准 |
| MCP server | 自己写 + 可选用官方 filesystem | Week 3 已练手 |

---

## ✅ 验收清单（按天）

### Day 22 设计
- [ ] DESIGN.md 9 个章节齐全
- [ ] 至少 2 张图（架构图 + 状态图）
- [ ] 测试集 ≥ 10 个问题写完

### Day 23-26 实现
- [ ] LangGraph 状态机能跑通基础对话
- [ ] RAG 工具：能根据问题检索到相关文档片段
- [ ] MCP 工具：能读写指定目录下的文件
- [ ] 长期记忆：重启服务后用户偏好仍在

### Day 27 评估（关键）
- [ ] 跑 10 个测试问题
- [ ] 每个问题在 LangSmith 上有完整 trace
- [ ] 至少识别 2 处可优化点（prompt / chunking / 工具描述）
- [ ] 优化后再跑一次，记录改进数据

### Day 28 接口
- [ ] `POST /chat`、`POST /upload`、`GET /memory` 至少 3 个 endpoint
- [ ] curl / Postman 验证可用
- [ ] 错误处理（LLM 超时、工具失败）

### Day 29-30 包装（**简历素材**）
- [ ] README 含：项目简介、架构图、运行方式、API 示例、技术亮点
- [ ] GitHub 仓库公开，README 有徽章
- [ ] 5 分钟讲解视频（讲架构 + demo）
- [ ] 复盘博客 1500 字（踩坑 + 收获 + 改进方向）

---

## 📝 简历素材清单（30 天后你应该有的）

```
GitHub:
  └─ knowledge-agent (公开)
      ├─ README.md (含架构图、demo gif)
      ├─ DESIGN.md
      └─ 完整代码

Blog (掘金/知乎/个人博客):
  ├─ 我理解的 ReAct 范式 (Week 1)
  ├─ HelloAgents vs LangGraph 对比 (Week 2)
  ├─ Agent RAG 实战 (Week 3)
  └─ 从 0 构建知识库 Agent (Week 4)

简历技能栏可写:
  Agent 开发：LangGraph、ReAct、MCP、Prompt Engineering
  RAG：ChromaDB、Embedding、Chunking 策略
  可观测性：LangSmith Tracing、Prompt 优化
  后端：FastAPI、SQLite、Python

简历项目栏可写:
  本地知识库 Agent
  - 基于 LangGraph 构建状态化 Agent，支持 ReAct 循环与多工具调用
  - 集成 ChromaDB 实现 RAG 检索增强，自定义 chunking 策略提升召回 X%
  - 自研 MCP server 实现本地文件读写工具
  - 通过 LangSmith Tracing 定位 prompt 缺陷，优化后 token 消耗降低 X%
  - 长期记忆模块持久化用户偏好，跨会话生效
  - FastAPI 包装为 HTTP 服务，Postman 可调
```

---

## 🎓 项目通过标准

不是"能跑"，而是：
1. ✅ 一个**没看过你代码**的人，能根据 README 在 10 分钟内跑起来
2. ✅ 你能**口述**项目从架构到细节，**不超过 5 分钟**讲完一遍
3. ✅ 面试官问"你这个项目难点是什么"，你能讲出 3 个真实的踩坑

---

## 🔗 资源

- 教程参考：`code/chapter13/helloagents-trip-planner/`（架构借鉴，不抄代码）
- LangGraph + RAG: https://langchain-ai.github.io/langgraph/tutorials/rag/
- 本周设计文档模板：[project-design-template.md](./project-design-template.md)

---

*[返回总计划](../README.md)*

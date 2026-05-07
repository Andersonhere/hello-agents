# Hello-Agents 学习进度统计

> 生成时间：2026-05-07
> 学习周期：30天计划

---

## 📊 总体进度概览

```
┌────────────────────────────────────────────────────────────────────────┐
│                        学习进度总览                                      │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  Week 1 ████████████████████████████████████████ 100% ✅ 已完成         │
│  Week 2 ████████████████████░░░░░░░░░░░░░░░░░░░░  50% 🔄 进行中         │
│  Week 3 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% ⬜ 未开始         │
│  Week 4 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% ⬜ 未开始         │
│                                                                        │
│  总体进度: ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░  38%                  │
│                                                                        │
│  已学习天数: 9 天 / 30 天                                               │
│  已投入时间: 约 13 小时                                                 │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📅 周度进度详情

### Week 1: 环境搭建 + 快速入门 ✅ 100%

📄 [详细进度](./week1/progress.md) | 📝 [学习笔记](./week1/notes/)

| 阶段 | 状态 | 完成率 | 核心任务 |
|------|------|--------|----------|
| Day 1-2 | ✅ 完成 | 100% | 环境配置、第一个 Agent |
| Day 3-4 | ✅ 完成 | 100% | Agent 基础、工具添加 |
| Day 5-7 | ✅ 完成 | 100% | ReAct/Reflection/Plan-Solve 范式 |

**关键成果**：
- ✅ Python 3.13 + venv 环境搭建
- ✅ scnet 平台 LLM 连接成功
- ✅ 运行三种范式示例代码
- ✅ 添加自定义工具 (get_time)
- ✅ 设计组合范式 HybridAgent

**学习笔记**：
- [Day 1-2 环境配置](./week1/notes/day1-2.md)
- [Day 3-4 第一个Agent](./week1/notes/day3-4.md)
- [Day 5-7 ReAct范式](./week1/notes/day5-7.md)
- [Week 1 总结](./week1/notes/week1-summary.md)

---

### Week 2: HelloAgents + LangGraph 双修 🔄 50%

📄 [详细进度](./week2/progress.md) | 📝 [学习笔记](./week2/notes/) | 📋 [v2 计划](./week2/plan.md)

> **⚠️ 计划已 v2 修订**：原"主流框架体验"改为"LangGraph 专攻 + 手写极简版"，详见 `week2/plan.md`

| 阶段 | 状态 | 完成率 | 核心任务 |
|------|------|--------|----------|
| Day 8 源码精读 | ✅ 完成 | 100% | HelloAgents 三个核心类 |
| Day 9 手写 mini SimpleAgent | ✅ 完成 | 100% | ≤50 行手写版 + 官方对比 |
| Day 10 手写 mini ReActAgent | 🔄 待开始 | 0% | ≤80 行 + 工具循环 |
| Day 11 LangGraph 入门 | ⬜ 未开始 | 0% | StateGraph / Node / Edge |
| Day 12 LangGraph 进阶 | ⬜ 未开始 | 0% | 条件边 + checkpointer |
| Day 13 双框架实现 ReAct | ⬜ 未开始 | 0% | 同一问题两套实现 |
| Day 14 对比博客 + 周复盘 | ⬜ 未开始 | 0% | **第 1 篇简历博客** |

**Day 9 关键成果**（2026-05-07，约 4h）：
- ✅ 不看源码独立写出 `mini_simple_agent.py`（25 行实现）
- ✅ 三个测试全部通过：基础问答、多轮上下文、reset 后失忆
- ✅ 安全规范：API key 迁移到 `.env` + `python-dotenv`，已确认未泄露
- ✅ 与官方 `SimpleAgent` 对比，识别 4 项工程必要 + 3 项锦上添花
- ✅ 5 题预测官方设计：Q1/Q3 命中，Q2/Q4/Q5 修正认知盲区
- 💡 核心洞察：**Agent 的"记忆"不是模型自带，是开发者拼接 messages 拼出来的**

**📂 产出文件**：
- `code/week2/mini_simple_agent.py` —— 手写极简版（含 3 题复盘）
- `week2/notes/day9-practice.md` —— 5 题预测对照笔记

---

### 🎯 明天 Day 10 任务（独立体现）

**主题**：手写极简版 ReActAgent —— 让 Agent 学会"思考-行动-观察"循环

**目标产出**：`code/week2/mini_react_agent.py`（≤80 行）

**核心要求**：
- ⬜ 实现 ReAct prompt 模板（Thought / Action / Observation 三段式）
- ⬜ 实现工具注册：注入 2 个 mock 工具（`get_weather`、`calculate`）
- ⬜ 实现解析循环：从 LLM 输出里提取 Action，调工具，把 Observation 拼回 prompt
- ⬜ 实现迭代上限（防死循环，参考 Day 9 对比中学到的 `max_iterations`）
- ⬜ 跑通测试题："北京今天的温度乘以 2 等于多少？"（必须用到两个工具）

**预期收获**：
- 真正理解 ReAct 不是魔法，而是 **prompt 约定 + 字符串解析 + 循环**
- 体会"为什么需要 max_iterations"——亲自踩一次死循环
- 为 Day 11 LangGraph 做铺垫（LangGraph 的 ToolNode 就是把这套循环抽象掉）

**开工前阅读**：
- `learning-plan/week2/plan.md` Day 10 章节
- 我会在你开始前提供 `mini_react_agent.py` 骨架提示卡

**预计时间**：4h（拆分：30min 周回顾 / 90min 手写 / 60min 跑通调试 / 60min 对比官方 + 笔记）

---

**Week 2 后续节奏**：
- Day 11-12：LangGraph 入门 + 进阶
- Day 13：双框架实现同一 ReAct Agent
- Day 14：写**第 1 篇博客**——双框架对比（800 字，简历素材）

**学习笔记**：
- [框架架构总结](./week2/notes/day8-10-framework.md)
- [实践记录](./week2/notes/day8-10-practice.md)

---

### Week 3: 高级主题 + MCP 协议 ⬜ 0%

📄 [详细进度](./week3/progress.md) | 📝 [学习笔记](./week3/notes/)

| 阶段 | 状态 | 完成率 | 核心任务 |
|------|------|--------|----------|
| Day 15-18 | ⬜ 未开始 | 0% | MCP 协议集成 |
| Day 19-21 | ⬜ 未开始 | 0% | 记忆系统、RAG |

---

### Week 4: 项目实战 ⬜ 0%

📄 [详细进度](./week4/progress.md) | 📝 [学习笔记](./week4/notes/)

| 阶段 | 状态 | 完成率 | 核心任务 |
|------|------|--------|----------|
| Day 22-28 | ⬜ 未开始 | 0% | 综合项目开发 |
| Day 29-30 | ⬜ 未开始 | 0% | 项目完善、毕业设计 |

---

## 🎯 里程碑追踪

| 时间节点 | 里程碑 | 状态 | 完成日期 |
|----------|--------|------|----------|
| Day 2 | 环境配置完成，第一个 Agent 运行成功 | ✅ | 2025-05-05 |
| Day 7 | 理解 ReAct 范式，能解释执行流程 | ✅ | 2025-05-05 |
| Day 10 | 掌握 HelloAgents 框架基本用法 | 🔄 | - |
| Day 14 | 能使用框架创建简单 Agent | ⬜ | - |
| Day 18 | 完成 MCP 工具集成 | ⬜ | - |
| Day 21 | 理解 RAG 基本原理 | ⬜ | - |
| Day 28 | 完成综合项目 | ⬜ | - |
| Day 30 | 完成毕业设计 | ⬜ | - |

---

## 📈 学习统计

### 时间投入

```
Week 1:  ████████ 6.5 小时
Week 2:  ███░░░░░ 2.5 小时 (进行中)
Week 3:  ░░░░░░░░ 0 小时
Week 4:  ░░░░░░░░ 0 小时
────────────────────────
总计:    ████████ 9 小时
```

### 任务完成情况

| 周次 | 总任务 | 已完成 | 进行中 | 未开始 | 完成率 |
|------|--------|--------|--------|--------|--------|
| Week 1 | 22 | 21 | 0 | 1 | 95% |
| Week 2 | 14 | 4 | 3 | 7 | 29% |
| Week 3 | 12 | 0 | 0 | 12 | 0% |
| Week 4 | 10 | 0 | 0 | 10 | 0% |
| **总计** | **58** | **25** | **3** | **30** | **43%** |

### 代码运行记录

| 代码文件 | 状态 | 运行次数 |
|----------|------|----------|
| first_agent.py | ✅ 成功 | 5+ |
| ReAct_demo.py | ✅ 成功 | 3 |
| Reflection.py | ✅ 成功 | 2 |
| Plan_and_solve.py | ✅ 成功 | 2 |
| test_llm_simple.py | ✅ 成功 | 1 |
| test_simple_agent.py | ✅ 成功 | 1 |

---

## 📚 已覆盖知识点

### 已掌握 ✅

- [x] Agent 定义和分类
- [x] Agent 核心组件 (LLM + Memory + Tools + Planning)
- [x] ReAct 范式 (Thought → Action → Observation)
- [x] Reflection 范式 (自我反思改进)
- [x] Plan-and-Solve 范式 (任务分解执行)
- [x] 工具定义和注册
- [x] HelloAgents 框架架构
- [x] HelloAgentsLLM 核心类
- [x] SimpleAgent 核心类
- [x] ToolRegistry 工具注册表

### 进行中 🔄

- [ ] ReActAgent 完整测试
- [ ] 自定义 Agent 创建
- [ ] 框架源码深入理解

### 未开始 ⬜

- [ ] MCP 协议集成
- [ ] A2A 智能体通信
- [ ] 记忆系统
- [ ] RAG 检索增强
- [ ] 综合项目开发

---

## 🏆 成就解锁

| 成就 | 描述 | 解锁时间 |
|------|------|----------|
| 🎉 第一步 | 成功运行第一个 Agent | 2025-05-05 |
| 🔧 工具大师 | 添加自定义工具 | 2025-05-05 |
| 🧠 范式专家 | 掌握三种经典范式 | 2025-05-05 |
| 🏗️ 架构师 | 理解框架核心架构 | 2025-05-05 |
| 🔗 连接者 | LLM 连接测试成功 | 2025-05-05 |
| 🤖 Agent工程师 | SimpleAgent 测试成功 | 2025-05-05 |
| ✍️ 极简手艺人 | 不看源码手写 mini_simple_agent | 2026-05-07 |
| 🔐 安全意识 | API key 迁移到 .env，避免泄露 | 2026-05-07 |
| 🔍 对比专家 | 7 维度对比手写版 vs 官方版 | 2026-05-07 |

---

## 📝 下一步行动（已对齐 v2 计划）

### ✅ Day 9 已完成（2026-05-07，约 4h）

- [x] 30 min 周回顾
- [x] 75 min 手写 `mini_simple_agent.py`（25 行实现）
- [x] 60 min 对照官方源码识别差异
- [x] 60 min 5 题预测对比 + 文件末 3 题复盘
- [x] 安全规范：API key 迁移到 `.env`

### 🎯 立即开始：Day 10 手写极简版 ReActAgent

- [ ] 30 min 复习 Week 1 ReAct 范式（Thought/Action/Observation）
- [ ] 90 min **不看源码**手写 `mini_react_agent.py`（≤80 行）
- [ ] 60 min 跑通"北京温度乘以 2"测试 + 调试 max_iterations
- [ ] 60 min 对照官方 `MyReActAgent`，更新笔记

### Day 11-14 后续

- [ ] Day 11：LangGraph 入门（StateGraph、Node、Edge）
- [ ] Day 12：LangGraph 进阶（条件边、checkpointer）
- [ ] Day 13：双框架实现同一 ReAct Agent
- [ ] Day 14：写**第 1 篇博客**——双框架对比（800 字）

### Week 2 关键产出（简历素材）

- [x] `code/week2/mini_simple_agent.py` ✅ Day 9
- [ ] `code/week2/mini_react_agent.py`
- [ ] `code/week2/langgraph_react_agent.py`
- [ ] `blogs/week2-framework-comparison.md`（博客）

---

*报告生成时间：2026-05-07*
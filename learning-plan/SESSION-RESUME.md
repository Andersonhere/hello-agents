# 学习会话衔接指南

> 本文件帮助你在新会话中快速恢复学习进度

---

## 🚀 新会话快速启动

### 方式一：直接复制提示词

复制以下内容到新会话：

```
我正在学习 Hello-Agents 智能体教程，请帮我继续学习。

## 当前状态
- 学习进度：Week 2 Day 8-10（框架实践）
- 已完成：Week 1 全部内容，Week 2 框架架构总结

## 我的请求
1. 先阅读 learning-plan/progress-report.md 了解总体进度
2. 阅读 learning-plan/week2/progress.md 了解本周详细进度
3. 继续之前的学习任务

## 重要规则
- 所有代码在 learning-plan/workspace/ 目录运行
- 环境变量在 learning-plan/workspace/.env
- 虚拟环境：source learning-plan/workspace/venv/bin/activate
- LLM: Qwen3-235B-A22B (scnet 平台)
```

### 方式二：指定具体任务

如果你想继续特定任务，使用：

```
我正在学习 Hello-Agents 智能体教程。

当前进度：Week 2 Day 8-10

请帮我：
1. 阅读 learning-plan/week2/progress.md 了解进度
2. 继续 [具体任务名称]

环境配置：
- 工作目录：learning-plan/workspace/
- 虚拟环境：source learning-plan/workspace/venv/bin/activate
- LLM：Qwen3-235B-A22B
```

---

## 📁 关键文件索引

### 进度文件

| 文件 | 用途 |
|------|------|
| `progress-report.md` | 总进度报告 |
| `week1/progress.md` | Week 1 详细进度 |
| `week2/progress.md` | Week 2 详细进度 |
| `week3/progress.md` | Week 3 详细进度 |
| `week4/progress.md` | Week 4 详细进度 |

### 学习笔记

| 周次 | 笔记目录 |
|------|----------|
| Week 1 | `week1/notes/` |
| Week 2 | `week2/notes/` |
| Week 3 | `week3/notes/` |
| Week 4 | `week4/notes/` |

### 规则文件

| 文件 | 用途 |
|------|------|
| `CLAUDE.md` | 项目规则（工作目录、环境配置） |
| `RULES.md` | 详细规则（代码复制、问题处理） |

---

## 📋 各阶段快速启动

### Week 2: 框架实践

```
继续 Week 2 学习，当前在 Day 8-10。

请帮我：
1. 阅读 learning-plan/week2/progress.md
2. 继续测试 ReActAgent / 创建自定义 Agent
```

### Week 3: MCP 协议

```
开始 Week 3 学习，主题是 MCP 协议集成。

请帮我：
1. 阅读 learning-plan/week3/progress.md
2. 总结 MCP 协议核心概念
3. 运行 MCP 工具示例
```

### Week 4: 项目实战

```
开始 Week 4 项目实战。

请帮我：
1. 阅读 learning-plan/week4/progress.md
2. 分析项目选项，推荐适合的方向
3. 设计项目架构
```

---

## 🔧 环境配置速查

```bash
# 激活虚拟环境
source /Users/gaoqi/wkspace/hello-agents/learning-plan/workspace/venv/bin/activate

# 工作目录
cd /Users/gaoqi/wkspace/hello-agents/learning-plan/workspace/code/

# 环境变量位置
learning-plan/workspace/.env
```

### LLM 配置

```
LLM_MODEL_ID=Qwen3-235B-A22B
LLM_API_KEY=sk-Njk4LTExNDk5MDYzM...
LLM_BASE_URL=https://api.scnet.cn/api/llm/v1
```

---

## 📝 学习记录模板

每次学习结束后，建议更新以下文件：

### 1. 更新周进度

```markdown
## [日期] 学习记录

- 完成任务：[任务列表]
- 遇到问题：[问题描述]
- 解决方案：[解决方法]
- 心得体会：[学习心得]
```

### 2. 更新笔记

在对应周的 `notes/` 目录下创建或更新笔记文件。

---

## 💡 高效衔接技巧

1. **每次结束前**：更新 `weekX/progress.md` 的状态
2. **记录问题**：在 `progress.md` 的问题表格中记录
3. **标记待办**：在 `待办事项` 部分列出下次要做的任务
4. **写简短总结**：在会话结束前让 AI 帮你总结本次学习内容

---

*创建时间：2026-05-06*
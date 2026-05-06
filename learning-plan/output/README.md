# Week 1 学习产出

> **学习周期**：2025-05-05
> **主题**：环境搭建 + 快速入门 + ReAct 范式

---

## 📁 目录结构

```
output/
├── README.md           # 本文件
├── progress.md         # 学习进度跟踪
├── code/               # 代码产出
│   ├── first_agent.py      # 第一个 Agent（带5次改进）
│   ├── ReAct_demo.py       # ReAct 范式演示（含自定义工具）
│   ├── ReAct.py            # ReAct 原始实现
│   ├── Plan_and_solve.py   # Plan-and-Solve 范式
│   ├── Reflection.py       # Reflection 范式
│   ├── HybridAgent.py      # 组合范式 Agent
│   ├── llm_client.py       # LLM 客户端封装
│   └── tools.py            # 工具定义
└── notes/              # 学习笔记
    ├── day1-2.md           # 环境配置 + 第一个 Agent
    ├── day3-4.md           # Agent 执行流程分析
    ├── day5-7.md           # 三种范式对比
    └── week1-summary.md    # 周总结
```

---

## 🎯 学习成果

### 知识掌握

| 目标 | 状态 |
|------|------|
| 理解 Agent 定义和分类 | ✅ 已掌握 |
| 理解 Agent 核心组成 | ✅ 已掌握 |
| 理解 ReAct 循环流程 | ✅ 已掌握 |
| 对比三种范式区别 | ✅ 已掌握 |

### 技能掌握

| 目标 | 状态 |
|------|------|
| 配置开发环境 | ✅ 已掌握 |
| 运行示例代码 | ✅ 已掌握 |
| 添加自定义工具 | ✅ 已掌握 |

---

## 📝 核心产出

### 代码文件说明

| 文件 | 范式 | 说明 |
|------|------|------|
| `first_agent.py` | ReAct | 第一个 Agent，包含5次代码改进 |
| `ReAct_demo.py` | ReAct | 简化版 ReAct，添加了 get_time 工具 |
| `Plan_and_solve.py` | Plan-Solve | 规划-执行范式，解决多步推理问题 |
| `Reflection.py` | Reflection | 反思范式，实现代码迭代优化 |
| `HybridAgent.py` | 组合范式 | 结合三种范式的混合 Agent |

### 笔记文件说明

| 文件 | 内容 |
|------|------|
| `day1-2.md` | 环境配置过程、第一个 Agent 运行、5次代码改进记录 |
| `day3-4.md` | Agent 执行流程分析、ReAct 循环理解 |
| `day5-7.md` | 三种范式对比分析、适用场景、历史处理机制 |
| `week1-summary.md` | 周学习总结、知识梳理、下周计划 |

---

## 🔑 关键发现

### 三种范式对比

| 范式 | 核心流程 | 适用场景 |
|------|----------|----------|
| **ReAct** | Thought → Action → Observation | 需要外部工具交互 |
| **Plan-and-Solve** | Plan → Execute | 结构性强、可分解的任务 |
| **Reflection** | Execute → Reflect → Refine | 对结果质量要求高 |

### 历史处理机制

三种范式的**历史处理本质相同**——都是将历史追加到提示词中传递给 LLM，只是封装方式不同。

---

## 📊 统计数据

| 统计项 | 数值 |
|--------|------|
| 总投入时间 | 6.5 小时 |
| 完成任务数 | 21 / 22 |
| 运行代码次数 | 10 |
| 代码文件数 | 8 |
| 笔记文件数 | 4 |

---

*生成时间：2025-05-05*

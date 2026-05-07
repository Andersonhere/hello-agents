# 📁 学习计划目录结构

> 2026-05-07 重构 v2 后的标准结构。**优先看这个文件来定位资源**，而不是凭印象。

## 🗺️ 全图

```
learning-plan/
│
├── 📌 入口文件
│   ├── README.md              # 30 天计划总览
│   ├── STRUCTURE.md           # 本文件，目录指南
│   ├── progress-report.md     # 唯一进度面板（每日更新）
│   └── SESSION-RESUME.md      # 新会话恢复用提示词
│
├── 📚 weekN/                  # 每周计划与学习日志
│   ├── plan.md                # 当周计划（v2 已修订）
│   └── notes/                 # 每日学习日志（dayN-xxx.md）
│
├── 💻 code/                   # 所有代码（按周组织）
│   ├── shared/                # 跨周复用的工具/封装
│   ├── week1/                 # 三种范式 + first_agent
│   ├── week2/                 # 手写 mini_*.py + LangGraph 实现
│   │   └── source-study/      # 跟着教程读源码做的练习
│   ├── week3/                 # MCP / RAG / 记忆 / Tracing
│   └── week4/                 # 知识库 Agent 项目代码
│
├── 🚀 projects/               # 实际项目
│   └── knowledge-agent-design-template.md   # Day 22 设计文档模板
│
├── ✍️  blogs/                 # 4 篇简历博客（产出）
│
├── 🤖 meta/                   # AI 协作配置
│   ├── CLAUDE.md              # 给 AI 的项目协议
│   ├── RULES.md               # AI 行为规则
│   ├── prompts/               # 4 个常用提示词
│   └── templates/             # 笔记模板
│
├── ⚙️  env/                   # 环境配置
│   ├── requirements.txt       # Python 依赖
│   └── .env.example           # 环境变量模板（公开）
│
├── 🔒 .env                    # 实际环境变量（gitignored）
└── 🔒 workspace/venv/         # 虚拟环境（gitignored）
```

## 🎯 快速定位指南

| 我想找... | 去哪里 |
|-----------|--------|
| 今天做什么？ | `progress-report.md` 看"立即开始"区块 |
| 当周详细任务 | `weekN/plan.md` |
| 我写的学习日志 | `weekN/notes/dayN-*.md` |
| 我写的代码 | `code/weekN/` |
| AI 怎么协作 | `meta/CLAUDE.md` + `meta/RULES.md` |
| 卡壳要套提示词 | `meta/prompts/` |
| 写日志/笔记的模板 | `meta/templates/` |
| Week 4 项目代码 | `code/week4/` |
| Week 4 设计文档 | `projects/knowledge-agent-design-template.md`（模板） → `projects/knowledge-agent/DESIGN.md`（成品） |
| 我写过的博客 | `blogs/` |
| 怎么配环境 | `env/requirements.txt` + `env/.env.example` |

## 📝 工作流（每天遵循）

```
开机
  ↓
1. 打开 progress-report.md → 看今天该做什么
2. 打开 weekN/plan.md → 看今天的任务详情和验收标准
3. 复制 meta/templates/daily-log.md → weekN/notes/dayN-xxx.md
  ↓
4. 写代码到 code/weekN/
  ↓
5. 写日志到 weekN/notes/dayN-xxx.md
  ↓
6. 更新 progress-report.md（打勾、记时间、踩坑）
  ↓
7. git commit
关机
```

## 🚫 已废弃的路径（不要再用）

| 旧路径 | 新位置 |
|--------|--------|
| `workspace/code/chapterN/` | `code/weekN/` 或 `code/weekN/source-study/chapterN/` |
| `workspace/projects/` | `projects/`（仅保留实际在做的） |
| `workspace/notes/`、`workspace/tests/` | 已删除（一直为空） |
| `output/code/`、`output/notes/`、`output/projects/` | 已合并入 `code/` 和 `weekN/notes/` |
| `weekN/dayX-Y.md`（每周根散文件） | `weekN/notes/dayN-*.md` |
| `weekN/progress.md` | 唯一进度面板 `progress-report.md` |
| `ai-prompts/` | `meta/prompts/` |
| `templates/` | `meta/templates/` |
| `CLAUDE.md`、`RULES.md`（根目录） | `meta/CLAUDE.md`、`meta/RULES.md` |

## ⚠️ 重构后待办

- [ ] 各 `weekN/plan.md` 和 `meta/CLAUDE.md` 内的部分旧路径引用未逐一更新（学习时顺手改即可）
- [ ] `workspace/venv/` 仍保留（路径迁移有风险），未来重建 venv 时移到 `learning-plan/venv/`
- [ ] `code/` 各目录下未来加 README.md 索引

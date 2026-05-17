---
description: 把学习笔记/总结博客化并发布到个人 Jekyll 博客 (andersonhere.github.io)
---

# 个人博客发布流程

把 `learning-plan/` 下的学习笔记 / 周复盘 / 对比文章发布到个人博客。

---

## 0. 前置信息（永远不变）

- **博客仓库**：`/home/gaoqi/wkspace/andersonhere.github.io`
- **博客主题**：Jekyll yat
- **博文目录**：`_posts/`
- **文件名格式**：`YYYY-MM-DD-标题不带空格.md`（中文标题OK）
- **部署方式**：push 到 `master` 分支，GitHub Pages 自动 build（约 1-3 分钟）
- **博客地址**：https://andersonhere.github.io/

---

## 1. 选定要发布的笔记

跟用户确认要发布哪个 / 哪些文件。常见来源：

- `learning-plan/output/notes/week*-*.md`（专门写给博客的稿）
- `learning-plan/week*/notes/week*-summary.md`（周复盘，需要博客化改造）
- `learning-plan/week*/notes/day*-*.md`（单日笔记，通常需要大量改造，慎选）

---

## 2. 博客化改造（critical）

学习笔记直接发会显得"内部感太强"。改造原则：

### 必删内容（仅对学习者本人有意义）

- 任务完成统计表（X / Y 完成率）
- 时间投入表（计划 vs 实际）
- 自我评分（1-5）
- 待办清单 / 未完成任务说明
- 学习资源"待阅读"列表
- 内部路径引用（`learning-plan/code/...` 这类）
- 内部编号（"Day 12 踩的坑"应改成"我踩过的坑"）

### 必保留内容（对读者有价值）

- 核心知识点 + 对比表
- 踩坑实录 + 解决方案
- 顿悟 / 心得 / 类比
- 给同行的建议
- GitHub 学习仓库链接 (`https://github.com/Andersonhere/hello-agents`)

### 推荐改写

- 一级标题用 Markdown `#` 但 Jekyll 会自动把 front matter 里的 `title` 渲染为 H1，**正文不要再有顶层 `#`**，从 `##` 开始
- 内联引用其他博客时用 Jekyll 永久链接：`/posts/标题/`
- 句首避免"作为学习计划的一部分..."这种内部口吻

---

## 3. 写入 `_posts/` 并加 Jekyll front matter

文件路径：`/home/gaoqi/wkspace/andersonhere.github.io/_posts/YYYY-MM-DD-标题.md`

front matter 模板：

```yaml
---
title: 文章主标题（可加副标题用 — 分隔）
date: YYYY-MM-DD HH:MM:SS +0800
categories: [大类, 子类]
tags: [标签1, 标签2, 标签3]
---
```

**categories 命名规范**（参考博客已有）：

- 操作系统类：`[操作系统, OSTEP, 虚拟化]`
- 网络类：`[Linux网络, 深入理解Linux网络]`
- C++ 类：`[C++]` 或 `[C++, 工具链, MCP]`
- **Agent 类**：`[AI Agent, LangGraph]` 或 `[AI Agent, 入门]`

**tags 命名规范**：用具体技术名 / 关键词（如 `LangGraph` / `ReAct` / `Python` / `LLM` / `框架对比`）。

**date 写法**：以"完成笔记的日期"为准；如果同日发多篇用不同时分秒区分排序。

**excerpt_image**（可选，封面图）：博客已有的图在 `images/covers/`，新文章如果没有合适封面可省略。

---

## 4. 检查已有 categories（避免分类碎片化）

// turbo
```bash
grep -h "^categories:" /home/gaoqi/wkspace/andersonhere.github.io/_posts/*.md | sort -u
```

如果发现分类已有，**优先复用**（不要新建语义重复的分类）。

---

## 5. Commit + Push

在 `andersonhere.github.io` 仓库（不是 hello-agents 仓库！）执行：

```bash
cd /home/gaoqi/wkspace/andersonhere.github.io
git add _posts/
git status --short    # 确认只加了想加的文件
git commit -m "post: <标题简短版>

<2-3 行说明: 文章主题 / 核心论点>"
git push
```

提交规范：用 `post:` 前缀（参考已有 commit history）。

**推送是必需的** —— 用户已经显式要求过"发布到博客"。GitHub Pages 只在 push 后才 build。

---

## 6. 同步到学习仓库（可选但推荐）

如果原稿在 `hello-agents/learning-plan/output/notes/`，**博客化后的版本**也可以反向同步过去（保留原版 + 加博客 URL 注释）。

或在原稿末尾加一行：

```markdown
> 已发布到个人博客：[标题](https://andersonhere.github.io/posts/标题/)
```

---

## 7. 用户验证

告诉用户：

1. 文件已写入 `_posts/<filename>.md`
2. 已 commit 并 push 到 master
3. **等待 1-3 分钟** GitHub Pages 完成 build
4. 刷新 https://andersonhere.github.io/ 即可看到

---

## 8. 常见坑

| 坑 | 解决 |
|---|---|
| 改了 `learning-plan` 下的原稿但没改 `_posts/` | 必须分别 push 两个仓库 |
| `_posts/` 里日期 > 今天 | Jekyll 默认不发布"未来文章"，需在 `_config.yml` 设 `future: true` 或改日期 |
| 文件名含空格 | Jekyll 渲染 URL 会很丑，文件名用 `-` 分隔或直接连写 |
| categories 写成单数变量 | 必须是 `[a, b]` 数组形式 |
| 正文有顶层 `# 标题` | 会和 front matter 的 title 重复显示，从 `##` 开始 |
| 改完忘了 push | `cd /home/gaoqi/wkspace/andersonhere.github.io && git status` 检查 |

---

## 9. 已发布文章模式参考（截至 2026-05-17）

| 日期 | 文件 | 类型 |
|---|---|---|
| 2025-05-05 | `Agent入门第一周-三种经典范式精读.md` | 入门科普 |
| 2026-05-17 | `LangGraph核心概念笔记-从手写Agent到Time-Travel.md` | 知识速查 |
| 2026-05-17 | `写完同一个Agent两遍后我才懂LangGraph在卷什么.md` | 论点对比 |

**风格基线**：标题有钩子 + 正文带数据/对比表 + 结尾给学习仓库链接。

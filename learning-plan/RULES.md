# 学习规则与注意事项

> 本文件记录学习过程中的重要规则，避免重复犯错

---

## 一、工作目录规则

### ⚠️ 代码运行目录

**所有学习代码都在 `learning-plan/workspace/` 目录下运行，不要污染原项目代码！**

```
正确目录：/Users/gaoqi/wkspace/hello-agents/learning-plan/workspace/
错误目录：/Users/gaoqi/wkspace/hello-agents/code/           ❌ 原项目代码，只读
```

### 目录结构

```
learning-plan/
├── workspace/                    # 工作目录（所有代码在这里运行）
│   ├── .env                      # 环境变量配置
│   ├── venv/                     # Python 虚拟环境
│   ├── code/                     # 学习代码
│   │   ├── chapter1/             # 第一章代码
│   │   ├── chapter4/             # 第四章代码
│   │   └── ...
│   └── requirements.txt
├── week1/                        # 学习计划
│   ├── notes/                    # 学习笔记
│   └── progress.md               # 进度跟踪
└── RULES.md                      # 本文件
```

---

## 二、环境配置规则

### Python 环境

```bash
# 激活虚拟环境
source /Users/gaoqi/wkspace/hello-agents/learning-plan/workspace/venv/bin/activate

# 运行代码
python xxx.py
```

### 环境变量

位置：`learning-plan/workspace/.env`

```
LLM_MODEL_ID=Qwen3-235B-A22B
LLM_API_KEY=sk-Njk4LTExNDk5MDYzMjM1LTE3NzMyODAzMzQzMzI=
LLM_BASE_URL=https://api.scnet.cn/api/llm/v1
LLM_TIMEOUT=60
TAVILY_API_KEY=                    # 待配置
```

---

## 三、代码复制规则

当需要运行原项目代码时：

```bash
# 1. 创建目标目录
mkdir -p /Users/gaoqi/wkspace/hello-agents/learning-plan/workspace/code/chapterX/

# 2. 复制代码文件
cp /Users/gaoqi/wkspace/hello-agents/code/chapterX/*.py /Users/gaoqi/wkspace/hello-agents/learning-plan/workspace/code/chapterX/

# 3. 在工作目录运行
cd /Users/gaoqi/wkspace/hello-agents/learning-plan/workspace/code/chapterX/
python xxx.py
```

---

## 四、笔记更新规则

### 笔记文件位置

- `learning-plan/week1/notes/day1-2.md` - 环境配置
- `learning-plan/week1/notes/day3-4.md` - 第一个 Agent
- `learning-plan/week1/notes/day5-7.md` - ReAct 范式

### 更新时机

- 完成每个阶段学习后立即更新笔记
- 记录运行结果、问题、心得体会
- 更新 `progress.md` 进度跟踪

---

## 五、常见问题处理

### 问题1：模块找不到

```bash
# 确保虚拟环境已激活
source /Users/gaoqi/wkspace/hello-agents/learning-plan/workspace/venv/bin/activate

# 安装缺失依赖
pip install xxx
```

### 问题2：API 调用失败

- 检查 `.env` 文件中的 API Key 是否正确
- 检查网络连接
- 检查 API 配额是否充足

### 问题3：工具依赖缺失（如 SerpApi）

- 创建简化版本绕过外部依赖
- 或者配置相应的 API Key

---

## 六、学习流程规范

```
1. 阅读文档 → 理解理论
2. 复制代码到 workspace → 运行验证
3. 记录笔记 → 巩固理解
4. 更新进度 → 跟踪状态
```

---

*最后更新：2025-05-05*

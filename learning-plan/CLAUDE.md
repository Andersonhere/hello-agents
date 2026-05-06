# CLAUDE.md - 学习项目规则

本项目是 hello-agents 教程的学习实践目录，请遵循以下规则：

## 核心规则

### ⚠️ 工作目录
**所有代码在 `workspace/` 目录下运行，不要修改原项目代码！**

```
✅ 正确：learning-plan/workspace/code/chapterX/
❌ 错误：hello-agents/code/chapterX/  （原项目，只读）
```

### 环境配置
```bash
# 激活虚拟环境
source learning-plan/workspace/venv/bin/activate

# 环境变量位置
learning-plan/workspace/.env
```

### 目录结构
```
learning-plan/
├── workspace/          # 工作目录（代码在这里运行）
│   ├── .env           # 环境变量
│   ├── venv/          # 虚拟环境
│   └── code/          # 学习代码
├── week1/             # 学习计划
│   └── notes/         # 学习笔记
└── RULES.md           # 详细规则
```

### LLM 配置
- 模型：Qwen3-235B-A22B
- 平台：scnet (https://api.scnet.cn/api/llm/v1)
- API Key 已配置在 .env 中

## 学习流程
1. 阅读 docs 文档理解理论
2. 复制代码到 workspace/code/ 目录
3. 运行验证并记录结果
4. 更新学习笔记和进度

## 详细规则
参见 [RULES.md](./RULES.md)

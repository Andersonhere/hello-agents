# 开发学习工作区

> 本目录用于实际开发学习，避免污染项目原始代码

---

## 📁 目录结构

```
workspace/
├── code/           # 学习代码
│   ├── chapter1/   # 第一章代码实践
│   ├── chapter4/   # 第四章代码实践
│   ├── chapter7/   # 第七章代码实践
│   └── chapter10/  # 第十章代码实践
│
├── projects/       # 项目开发
│   ├── search-agent/        # 搜索助手
│   ├── mcp-agent/          # MCP Agent
│   └── travel-assistant/   # 旅行助手
│
├── tests/          # 测试代码
│
├── notes/          # 开发笔记
│
└── .env            # 环境配置（需自己创建）
```

---

## 🚀 快速开始

### 1. 创建环境配置

```bash
# 进入工作区
cd /Users/gaoqi/wkspace/hello-agents/learning-plan/workspace

# 创建 .env 文件
cat > .env << 'EOF'
# LLM 配置
LLM_MODEL_ID=your-model
LLM_API_KEY=your-api-key
LLM_BASE_URL=your-base-url
LLM_TIMEOUT=60

# 工具 API
TAVILY_API_KEY=your-tavily-key
EOF

# 编辑 .env 文件，填入你的 API 密钥
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install openai tavily-python python-dotenv requests
pip install "hello-agents[protocols]>=0.2.4,<=0.2.9"
pip install fastapi uvicorn pydantic
```

### 3. 创建代码目录

```bash
# 创建各章节代码目录
mkdir -p code/{chapter1,chapter4,chapter7,chapter10}
mkdir -p projects/{search-agent,mcp-agent,travel-assistant}
```

---

## 📝 使用说明

### 学习代码

在学习各章节时，将代码复制到对应的 `code/chapterX/` 目录进行实验：

```bash
# 例如：复制第一章代码到工作区
cp ../code/chapter1/FirstAgentTest.py code/chapter1/

# 运行代码
cd code/chapter1
python FirstAgentTest.py
```

### 项目开发

在 `projects/` 目录下开发自己的项目：

```bash
# 例如：创建搜索助手项目
cd projects/search-agent
touch main.py
```

### 测试代码

在 `tests/` 目录下编写和运行测试：

```bash
cd tests
python test_xxx.py
```

---

## 📋 学习阶段对照

| 学习阶段 | 工作目录 | 说明 |
|----------|----------|------|
| Week 1 | `code/chapter1/` | 第一个 Agent |
| Week 1 | `code/chapter4/` | ReAct 范式 |
| Week 2 | `code/chapter7/` | HelloAgents 框架 |
| Week 2 | `projects/search-agent/` | 搜索助手项目 |
| Week 3 | `code/chapter10/` | MCP 协议 |
| Week 3 | `projects/mcp-agent/` | MCP Agent 项目 |
| Week 4 | `projects/travel-assistant/` | 旅行助手项目 |

---

## ⚠️ 注意事项

1. **不要修改项目原始代码**：所有实验代码都在 workspace 中进行
2. **.env 文件不要提交**：包含敏感信息
3. **定期清理**：完成学习后可以清理 workspace
4. **虚拟环境**：建议每个项目使用独立的虚拟环境

---

## 🔗 相关链接

- [学习计划总览](../README.md)
- [Week 1 计划](../week1/plan.md)
- [AI 提示词库](../ai-prompts/)

---

*创建日期：2024*

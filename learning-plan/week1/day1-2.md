# Day 1-2：环境配置

> **目标**：完成开发环境搭建，获取必要的 API 密钥
> **产出**：可运行的开发环境 + 配置完成的 `.env` 文件

---

## 📋 今日任务清单

| 序号 | 任务 | 类型 | 预计时间 | 状态 |
|------|------|------|----------|------|
| 1 | Python 环境检查 | 🧠 自主 | 10分钟 | ⬜ |
| 2 | 创建虚拟环境 | 🧠 自主 | 10分钟 | ⬜ |
| 3 | 获取 LLM API 密钥 | 🧠 自主 | 20分钟 | ⬜ |
| 4 | 获取 Tavily API 密钥 | 🧠 自主 | 10分钟 | ⬜ |
| 5 | 创建 .env 配置文件 | 🧠 自主 | 10分钟 | ⬜ |
| 6 | 安装核心依赖 | 🧠 自主 | 15分钟 | ⬜ |
| 7 | 验证环境配置 | 🧠 自主 | 15分钟 | ⬜ |
| 8 | 记录学习笔记 | 🧠 自主 | 10分钟 | ⬜ |

**总计时间：约 1.5 小时**

---

## 🎯 任务详情

### 任务 1：Python 环境检查

**你需要做的事情** 🧠：

```bash
# 检查 Python 版本
python --version
# 或
python3 --version

# 确保版本 >= 3.10
```

**如果版本过低**：
- Windows: 从 [python.org](https://www.python.org/downloads/) 下载安装
- macOS: `brew install python@3.10`
- Linux: `sudo apt install python3.10`

**AI 可以帮助的事情** 🤖：
> 提示词：我需要在 [Windows/macOS/Linux] 上安装 Python 3.10+，请给我详细的安装步骤

---

### 任务 2：创建虚拟环境

**你需要做的事情** 🧠：

```bash
# 进入项目目录
cd /Users/gaoqi/wkspace/hello-agents

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# 验证激活成功（命令行前面会有 (venv) 标识）
which python  # macOS/Linux
where python  # Windows
```

**AI 可以帮助的事情** 🤖：
> 提示词：虚拟环境激活后，我如何确认它正在使用？如何退出虚拟环境？

---

### 任务 3：获取 LLM API 密钥

**你需要做的事情** 🧠：

#### 选项一：AIHubmix（推荐新手）

1. 访问 [AIHubmix 官网](https://aihubmix.com/)
2. 注册账号（支持邮箱/手机号）
3. 访问 [模型中心](https://aihubmix.com/models)，筛选"免费"标签
4. 访问 [API 密钥管理](https://console.aihubmix.com/token) 获取密钥

**记录以下信息**：
```
API Key: sk-xxxxxxxx
Base URL: https://aihubmix.com/v1
推荐模型: coding-glm-4.7-free
```

#### 选项二：ModelScope（国内推荐）

1. 访问 [ModelScope](https://modelscope.cn/)
2. 注册并登录
3. 在个人中心获取 SDK 令牌
4. 先绑定阿里云账号（必须步骤）

**记录以下信息**：
```
API Key: 你的SDK令牌
Base URL: https://api-inference.modelscope.cn/v1/
推荐模型: Qwen/Qwen2.5-72B-Instruct
```

**AI 可以帮助的事情** 🤖：
> 提示词：AIHubmix 和 ModelScope 有什么区别？我应该如何选择？

---

### 任务 4：获取 Tavily API 密钥

**你需要做的事情** 🧠：

1. 访问 [Tavily 官网](https://tavily.com/)
2. 注册账号
3. 在控制台获取 API Key
4. 免费额度：1000次/月

**记录以下信息**：
```
TAVILY_API_KEY: tvly-xxxxxxxx
```

**AI 可以帮助的事情** 🤖：
> 提示词：Tavily API 是什么？在 Agent 中有什么作用？

---

### 任务 5：创建 .env 配置文件

**你需要做的事情** 🧠：

```bash
# 在项目根目录创建 .env 文件
cd /Users/gaoqi/wkspace/hello-agents
touch .env  # macOS/Linux
# 或在 Windows 中手动创建
```

**编辑 .env 文件内容**：

```env
# ============================================================================
# HelloAgents 统一环境变量配置文件
# ============================================================================

# ============================================================================
# 🚀 统一配置格式（推荐）- 框架自动检测provider
# ============================================================================

# 模型名称（根据你选择的平台填写）
LLM_MODEL_ID=coding-glm-4.7-free

# API密钥
LLM_API_KEY=your-api-key-here

# 服务地址（根据你选择的平台填写）
# AIHubmix:
LLM_BASE_URL=https://aihubmix.com/v1
# ModelScope:
# LLM_BASE_URL=https://api-inference.modelscope.cn/v1/

# 超时时间（可选，默认60秒）
LLM_TIMEOUT=60

# ============================================================================
# 🛠️ 工具配置
# ============================================================================

# Tavily Search API
TAVILY_API_KEY=your-tavily-key

# SerpApi（可选）
# SERPAPI_API_KEY=your-serpapi-key

# GitHub Token（可选）
# GITHUB_PERSONAL_ACCESS_TOKEN=your-github-token
```

---

### 任务 6：安装核心依赖

**你需要做的事情** 🧠：

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 安装核心依赖
pip install openai>=1.0.0
pip install tavily-python>=0.3.0
pip install python-dotenv>=1.0.0
pip install requests>=2.31.0

# 安装 HelloAgents 框架
pip install hello-agents>=0.2.4,<=0.2.9

# 或者一次性安装
pip install openai tavily-python python-dotenv requests "hello-agents>=0.2.4,<=0.2.9"
```

**AI 可以帮助的事情** 🤖：
> 提示词：pip install 时提示网络超时，我应该如何解决？（国内镜像源配置）

---

### 任务 7：验证环境配置

**你需要做的事情** 🧠：

创建测试文件 `test_env.py`：

```python
# test_env.py
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("=" * 50)
print("环境配置验证")
print("=" * 50)

# 检查环境变量
env_vars = [
    "LLM_MODEL_ID",
    "LLM_API_KEY",
    "LLM_BASE_URL",
    "TAVILY_API_KEY"
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        # 部分隐藏敏感信息
        masked = value[:8] + "****" + value[-4:] if len(value) > 12 else "****"
        print(f"✅ {var}: {masked}")
    else:
        print(f"❌ {var}: 未配置")

print("=" * 50)

# 测试 LLM API 连接
print("\n测试 LLM API 连接...")
try:
    from openai import OpenAI
    client = OpenAI(
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL")
    )
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL_ID"),
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print(f"✅ LLM API 连接成功: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ LLM API 连接失败: {e}")

# 测试 Tavily API 连接
print("\n测试 Tavily API 连接...")
try:
    from tavily import TavilyClient
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    result = tavily.search("test", search_depth="basic", max_results=1)
    print(f"✅ Tavily API 连接成功")
except Exception as e:
    print(f"❌ Tavily API 连接失败: {e}")

print("\n" + "=" * 50)
print("验证完成")
print("=" * 50)
```

运行测试：
```bash
python test_env.py
```

**AI 可以帮助的事情** 🤖：
> 提示词：运行 test_env.py 时报错 [粘贴错误信息]，请帮我分析原因并给出解决方案

---

### 任务 8：记录学习笔记

**你需要做的事情** 🧠：

创建学习笔记文件 `notes/day1-2-notes.md`：

```markdown
# Day 1-2 学习笔记

## 环境配置记录

### Python 版本
- 版本：
- 安装方式：

### API 配置
- [ ] LLM API (AIHubmix/ModelScope)
- [ ] Tavily API

### 遇到的问题
1. 
   - 解决方案：

### 心得体会
-

## 待解决问题
- [ ]
```

---

## 🤖 AI 辅助提示词

### 环境配置相关

```
我需要配置 Python 开发环境来学习 Hello-Agents 项目，请帮我：
1. 列出需要安装的所有依赖包及其作用
2. 解释每个环境变量的含义
3. 提供常见问题的解决方案
```

### 调试相关

```
我在配置环境时遇到以下错误：
[粘贴错误信息]

我的环境是：
- 操作系统：
- Python 版本：
- 已安装的包：

请帮我分析原因并提供解决方案。
```

### 概念理解

```
请简单解释以下概念：
1. 什么是 API Key？为什么需要它？
2. 什么是 Base URL？
3. 什么是虚拟环境？为什么要使用它？
```

---

## 🧠 自主学习重点

### 必须自己做的事情

| 事项 | 原因 |
|------|------|
| 亲自注册 API 账号 | 需要保管好自己的密钥 |
| 亲手配置 .env 文件 | 理解配置结构 |
| 手动运行测试代码 | 确保环境正确 |
| 记录配置过程 | 方便后续复现 |

### 需要理解的概念

| 概念 | 理解程度要求 |
|------|-------------|
| 虚拟环境 | 知道为什么用、怎么激活 |
| 环境变量 | 知道如何配置、如何读取 |
| API Key | 知道是什么、如何获取、如何保密 |
| pip 安装 | 知道如何安装、如何查看已安装 |

---

## ✅ 完成标准

今天的学习完成后，你应该：

- [ ] Python 版本 >= 3.10
- [ ] 虚拟环境创建成功并能激活
- [ ] 至少获取了一个 LLM API 密钥
- [ ] Tavily API 密钥获取成功
- [ ] .env 文件配置正确
- [ ] 所有依赖安装成功
- [ ] `test_env.py` 运行成功，所有测试通过
- [ ] 学习笔记已记录

---

## 📝 常见问题

### Q1: pip 安装速度慢？
```bash
# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple [包名]
```

### Q2: 虚拟环境激活失败？
- Windows: 确保使用 `venv\Scripts\activate`
- macOS/Linux: 确保使用 `source venv/bin/activate`
- 如果提示权限问题，尝试 `chmod +x venv/bin/activate`

### Q3: API 连接超时？
- 检查网络连接
- 检查 Base URL 是否正确
- 尝试使用代理

### Q4: 找不到模块？
- 确保虚拟环境已激活
- 重新安装依赖：`pip install -r requirements.txt`

---

*[返回周计划](./plan.md)*

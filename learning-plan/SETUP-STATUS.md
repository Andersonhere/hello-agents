# 环境部署状态（自动生成）

> 生成时间：2026-05-15 00:25
> 本机：Ubuntu 22.04 / Python 3.10.12

---

## ✅ 已完成

- 系统包：`python3.10-venv` / `python3-pip` 已安装（sudo apt）
- 虚拟环境：`learning-plan/env/venv/` 已重建
- 依赖：全部装好（清华镜像，约 1.5 分钟）
- `.env`：已从 `.env.example` 复制 —— **API key 还是占位符**
- **关卡 1（线性 graph）** 已用新 venv 跑通：`{'msg': 'say: hello world'}`

## 依赖版本

| 包 | 版本 |
|---|---|
| langgraph | 1.2.0 |
| langchain-core | 1.4.0 |
| openai | 1.109.1 |
| hello-agents | 0.2.9 |
| fastapi | 0.136.1 |
| pytest | 9.0.3 |
| huggingface_hub | 1.14.0 |

## ⚠️ 起床第一件事

**编辑 `learning-plan/.env` 把 `LLM_API_KEY` 填成真实值**（旧机器上是 `sk-Njk4LTExNDk5MDYzM...` 开头）：

```bash
nano learning-plan/.env
# 或
$EDITOR learning-plan/.env
```

## 激活环境

```bash
source learning-plan/env/venv/bin/activate
# 之后正常 python xxx.py
```

或者一行不激活：

```bash
learning-plan/env/venv/bin/python learning-plan/code/week2/langgraph_hello.py
```

## 下一步学习任务（Day 11 续）

- **关卡 2**：`langgraph_hello.py` 的 `test_level2()` —— 调 LLM 的 QA graph，**代码已写完**，填好 API key 即可跑
- **关卡 3**：用 LangGraph 重写 mini_react_agent —— `call_llm_node` / `call_tool_node` / `should_continue` / `build_react_graph` 还是 `pass`，待你实现

## 留存文件清单（受 git 追踪）

- `learning-plan/setup.sh` —— 部署脚本（支持 `--recreate` / `--deps-only`）
- `learning-plan/.env.example` —— 环境变量模板
- `learning-plan/SETUP-STATUS.md` —— 本文件

## 留存文件清单（gitignored，不入库）

- `learning-plan/env/venv/` —— 虚拟环境
- `learning-plan/env/requirements.txt` —— 依赖清单（已补 langgraph + huggingface_hub）
- `learning-plan/.env` —— 实际环境变量

## 换机器/重装命令

```bash
# 1. 系统级依赖（仅 Ubuntu 首次需要 sudo）
sudo apt install -y python3.10-venv python3-pip

# 2. 部署虚拟环境 + 安装依赖（清华镜像，约 1-2 分钟）
bash learning-plan/setup.sh

# 3. 编辑 .env 填真实 LLM_API_KEY
$EDITOR learning-plan/.env

# 4. （可选，推荐）安装 cd 进项目自动激活 venv 的 shell 钩子
bash learning-plan/setup.sh --install-shell-hook
source ~/.bashrc    # 当前终端立刻生效
```

### setup.sh 其它开关

```bash
bash learning-plan/setup.sh --recreate            # 删 venv 重建
bash learning-plan/setup.sh --deps-only           # 只装依赖（不动 .env）
bash learning-plan/setup.sh --install-shell-hook  # 仅装 shell 钩子，不部署
PIP_INDEX=https://pypi.org/simple bash learning-plan/setup.sh  # 换镜像
```

---

## Shell 自动激活钩子

`--install-shell-hook` 会在 `~/.bashrc` 末尾写入一段（用 `# >>> hello-agents auto venv >>>` / `# <<<` 包裹的）函数 + `PROMPT_COMMAND` 注入：

- **效果**：`cd` 进 `hello-agents` 任何子目录时自动 `source venv/activate`（提示符出现 `(venv)`），离开自动 `deactivate`
- **原理**：bash 每次显示提示符前会执行 `PROMPT_COMMAND`，钩子函数检查 `$PWD` 前缀并对比 `$VIRTUAL_ENV`，幂等切换
- **回滚**：手动删除 `~/.bashrc` 里 `# >>> hello-agents auto venv >>>` 到 `# <<< hello-agents auto venv <<<` 整段即可
- **二次执行安全**：函数检查 marker 是否已存在，存在则跳过，不会重复注入

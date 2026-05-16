#!/usr/bin/env bash
# ============================================================================
# Hello-Agents 学习环境部署脚本
# ----------------------------------------------------------------------------
# 用法：
#   bash learning-plan/setup.sh                # 全量部署（首次）
#   bash learning-plan/setup.sh --recreate     # 删掉旧 venv 重建
#   bash learning-plan/setup.sh --deps-only    # 只装/升级依赖
#   bash learning-plan/setup.sh --install-shell-hook
#                                              # 仅向 ~/.bashrc 注入 cd 进项目自动激活 venv 的钩子
#
# 产出：
#   learning-plan/env/venv/              # 虚拟环境（gitignored）
#   learning-plan/env/requirements.txt   # 依赖清单（gitignored）
#   learning-plan/.env                   # 实际 env（gitignored）—— 拷贝自 .env.example
#   ~/.bashrc 末尾追加 hello-agents 自动激活钩子（仅 --install-shell-hook）
# ============================================================================
set -euo pipefail

# 定位脚本所在目录（即 learning-plan/）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DIR="$SCRIPT_DIR/env"
VENV_DIR="$ENV_DIR/venv"
REQ_FILE="$ENV_DIR/requirements.txt"
ENV_FILE="$SCRIPT_DIR/.env"
ENV_EXAMPLE="$SCRIPT_DIR/.env.example"

RECREATE=0
DEPS_ONLY=0
INSTALL_HOOK=0
for arg in "$@"; do
  case "$arg" in
    --recreate)           RECREATE=1 ;;
    --deps-only)          DEPS_ONLY=1 ;;
    --install-shell-hook) INSTALL_HOOK=1 ;;
    -h|--help)
      sed -n '2,14p' "$0"; exit 0 ;;
    *) echo "[warn] 未知参数: $arg" ;;
  esac
done

# ----------------------------------------------------------------------------
# 子功能：向 ~/.bashrc 注入 "cd 进项目自动激活 venv" 钩子
# 原理：bash 每次显示提示符前执行 PROMPT_COMMAND，钩子函数检查 PWD 前缀，
#       匹配项目目录则 source venv/activate，离开则 deactivate。幂等安全。
# ----------------------------------------------------------------------------
install_shell_hook() {
  local PROJECT_ROOT
  PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
  local TARGET_VENV="$VENV_DIR"
  local MARKER="# >>> hello-agents auto venv >>>"
  local END_MARKER="# <<< hello-agents auto venv <<<"

  if grep -qF "$MARKER" "$HOME/.bashrc" 2>/dev/null; then
    echo "  ✅ 钩子已存在于 ~/.bashrc，跳过"
    return 0
  fi

  cat >> "$HOME/.bashrc" <<EOF

$MARKER
# hello-agents 项目：进入目录自动激活 venv，离开自动 deactivate
# 由 learning-plan/setup.sh --install-shell-hook 写入，可手动删除整段
_HELLO_AGENTS_ROOT="$PROJECT_ROOT"
_HELLO_AGENTS_VENV="$TARGET_VENV"
_hello_agents_auto_venv() {
    if [[ "\$PWD" == "\$_HELLO_AGENTS_ROOT"* ]]; then
        if [[ "\$VIRTUAL_ENV" != "\$_HELLO_AGENTS_VENV" ]]; then
            [[ -n "\$VIRTUAL_ENV" ]] && deactivate 2>/dev/null
            # shellcheck disable=SC1091
            source "\$_HELLO_AGENTS_VENV/bin/activate" 2>/dev/null
        fi
    else
        if [[ "\$VIRTUAL_ENV" == "\$_HELLO_AGENTS_VENV" ]]; then
            deactivate 2>/dev/null
        fi
    fi
}
PROMPT_COMMAND="_hello_agents_auto_venv;\${PROMPT_COMMAND:-}"
$END_MARKER
EOF
  echo "  ✅ 已写入 ~/.bashrc"
  echo "  ℹ️  立即生效：source ~/.bashrc  （或开新终端）"
}

if [ "$INSTALL_HOOK" = 1 ]; then
  echo "[hook] 安装 shell 自动激活钩子 ..."
  install_shell_hook
  echo "[hook] 完成"
  # 仅装钩子模式：不跑后续部署
  exit 0
fi

echo "[1/5] 检查系统 Python ..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "  ❌ 未找到 python3，请先安装 Python 3.10+"; exit 1
fi
PY_VER="$(python3 -c 'import sys;print("%d.%d"%sys.version_info[:2])')"
echo "  ✅ python3 = $(which python3)  ($PY_VER)"

# 检查 venv 模块可用
if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "  ❌ python3-venv 缺失，请执行: sudo apt install -y python${PY_VER}-venv"; exit 1
fi

echo "[2/5] 准备 env/ 目录 ..."
mkdir -p "$ENV_DIR"

if [ ! -f "$REQ_FILE" ]; then
  echo "  ❌ 缺少 $REQ_FILE"; exit 1
fi
echo "  ✅ requirements: $REQ_FILE"

echo "[3/5] 创建/复用虚拟环境 ..."
if [ "$RECREATE" = 1 ] && [ -d "$VENV_DIR" ]; then
  echo "  🗑️  删除旧 venv: $VENV_DIR"
  rm -rf "$VENV_DIR"
fi
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
  echo "  ✅ 已创建: $VENV_DIR"
else
  echo "  ✅ 已存在: $VENV_DIR"
fi

PIP="$VENV_DIR/bin/pip"
PY="$VENV_DIR/bin/python"

echo "[4/5] 安装依赖 ..."
# 可通过环境变量覆盖镜像：PIP_INDEX=https://pypi.org/simple bash setup.sh
PIP_INDEX="${PIP_INDEX:-https://pypi.tuna.tsinghua.edu.cn/simple}"
echo "  📦 使用镜像: $PIP_INDEX"
echo "  ⏳ 升级 pip / setuptools / wheel ..."
"$PY" -m pip install -i "$PIP_INDEX" --upgrade pip setuptools wheel
echo "  ⏳ 安装项目依赖（首次可能 3-10 分钟，请耐心等待进度条）..."
"$PIP" install -i "$PIP_INDEX" --progress-bar on -r "$REQ_FILE"
echo "  ✅ 依赖安装完成"

echo "[5/5] 准备 .env ..."
if [ "$DEPS_ONLY" = 1 ]; then
  echo "  ⏭️  --deps-only，跳过 .env 处理"
elif [ -f "$ENV_FILE" ]; then
  echo "  ✅ 已存在 $ENV_FILE，未覆盖"
elif [ -f "$ENV_EXAMPLE" ]; then
  cp "$ENV_EXAMPLE" "$ENV_FILE"
  echo "  ✅ 已从模板创建 $ENV_FILE —— 请编辑填入真实 LLM_API_KEY"
else
  echo "  ⚠️  未找到 $ENV_EXAMPLE，跳过"
fi

echo ""
echo "============================================================"
echo "✅ 部署完成"
echo ""
echo "下一步："
echo "  1. 编辑 .env 填入真实 API key:"
echo "       \$EDITOR $ENV_FILE"
echo "  2. 激活虚拟环境:"
echo "       source $VENV_DIR/bin/activate"
echo "  3. 运行示例:"
echo "       python learning-plan/code/week2/langgraph_hello.py"
echo "============================================================"

#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"

if [ ! -d .venv ]; then
  echo "创建虚拟环境 .venv ..."
  "$PYTHON" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install -r requirements.txt

# macOS: 使用系统证书库（truststore）

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "已创建 .env，请编辑后填入 OPENAI_API_KEY"
fi

echo "启动 Web 服务: http://localhost:8000"
python web_main.py

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

# macOS: 修复 Python SSL 证书问题
export SSL_CERT_FILE="$(python3 -c 'import certifi; print(certifi.where())')"
export REQUESTS_CA_BUNDLE="$SSL_CERT_FILE"

if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "已创建 .env，请编辑后填入 OPENAI_API_KEY"
fi

echo "启动 Web 服务: http://localhost:8000"
python web_main.py

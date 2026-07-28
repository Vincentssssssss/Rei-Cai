#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  echo ".env 已存在，跳过创建"
  exit 0
fi

if [ -f .env.example ]; then
  cp .env.example .env
  echo "已从 .env.example 创建 .env，请编辑后填入 OPENAI_API_KEY"
  exit 0
fi

cat > .env <<'EOF'
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=openai/qwen-plus
EOF

echo "已创建默认 .env，请编辑后填入 OPENAI_API_KEY"

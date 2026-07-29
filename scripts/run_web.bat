@echo off
setlocal
cd /d "%~dp0.."

if not exist .venv (
  echo Creating virtual environment .venv ...
  python -m venv .venv
)

call .venv\Scripts\activate.bat
pip install -r requirements.txt

if not exist .env if exist .env.example (
  copy .env.example .env
  echo Created .env - please edit OPENAI_API_KEY and OPENAI_BASE_URL
)

echo.
echo Starting Rei-Cai Web: http://localhost:8000
python web_main.py

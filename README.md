# Rei-Cai

基于资料学习的智能对话机器人。核心逻辑跨平台（Windows / macOS / Linux），**推荐用 Web 版**开发与测试，最终部署到 **Linux 服务器**。

## 平台选择建议

| 场景 | 推荐方式 | 说明 |
|------|----------|------|
| Windows 本地测试 | **Web 版** `web_main.py` | **不需要 Linux 虚拟机**，浏览器访问即可 |
| macOS 本地测试 | Web 版 或 桌面 GUI | 同左 |
| 演示 / 协作 | GitHub Codespaces | 浏览器访问 8000 端口 |
| **生产部署（长远）** | **Linux 服务器 + Web 版** | 与 Windows 开发用同一套代码 |

> 底层代码已用 `pathlib` 处理路径、Flask 提供 Web 界面，Windows 开发 → Linux 部署**无需改业务代码**，只需复制 `.env` 和 `data/` 目录。

## 功能

- **双入口界面**：首页提供「用户入口」与「管理入口」，无需登录认证
- **资料管理**：支持上传 `.txt`、`.md`、`.pdf` 文件
- **知识索引**：自动分块并建立 TF-IDF 检索索引
- **智能问答**：根据已上传资料检索相关内容并生成回答，附资料引用
- **可选 LLM**：配置 `OPENAI_API_KEY` 后可调用 OpenAI 兼容 API 生成更自然的回答

## 在 GitHub Codespaces 中展示（推荐）

Codespaces 没有桌面环境，请使用 Web 版本：

1. 打开仓库，点击 **Code → Codespaces → Create codespace**
2. 等待环境创建完成（会自动安装依赖并启动 Web 服务）
3. 在弹出的浏览器标签页访问 **8000 端口**，或点击 Ports 面板中的链接

手动启动：

```bash
pip install -r requirements.txt
python web_main.py
```

然后在 Codespaces 中打开转发的 `8000` 端口即可看到界面。

### 配置 API Key（Codespaces）

在 Codespaces 中打开终端，创建 `.env`：

```bash
git pull origin main          # 若提示找不到 .env.example，先拉取最新代码
bash scripts/setup_env.sh     # 或: cp .env.example .env
```

或在仓库 **Settings → Secrets and variables → Codespaces** 中添加：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL` = `https://llm-xxxxx.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`
- `OPENAI_MODEL` = `openai/qwen-plus`

## 本地 macOS 运行（Homebrew）

macOS 上通常没有 `python` 命令，请使用 `python3`：

```bash
cd Rei-Cai

# 1. 创建并激活虚拟环境（推荐）
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API Key（可选）
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY

# 4. 启动 Web 版
python3 web_main.py
```

浏览器打开 http://localhost:8000

或使用一键脚本：

```bash
bash scripts/run_web.sh
```

桌面 GUI 还需安装 tkinter：

```bash
brew install python-tk@3.14
python3 main.py
```

> 若 `pip install` 失败，可能是 Python 3.14 过新，可改用 3.12：
> `brew install python@3.12 && python3.12 -m venv .venv`

### macOS SSL 证书报错

若出现 `SSLError` 或 `CERTIFICATE_VERIFY_FAILED`：

```bash
cd Rei-Cai
source .venv/bin/activate
git pull origin main
pip install -r requirements.txt   # 含 truststore，自动使用 macOS 系统证书

python3 check_llm.py
python3 web_main.py
```

若仍失败，可临时跳过 SSL 验证做测试（不推荐长期使用）：

```bash
LLM_INSECURE_SSL=1 python3 web_main.py
```

LLM_INSECURE_SSL=1 python3 web_main.py
```

## Windows 本地运行

**不需要 Linux 虚拟机。** 安装 [Python 3.10+](https://www.python.org/downloads/)（勾选 *Add Python to PATH*）后：

```powershell
cd Rei-Cai
git clone https://github.com/Vincentssssssss/Rei-Cai.git
cd Rei-Cai

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
# 用记事本编辑 .env，填入 OPENAI_API_KEY 和 OPENAI_BASE_URL
notepad .env

python check_llm.py
python web_main.py
```

浏览器打开 http://localhost:8000

或双击运行（需先装好 Python）：

```text
scripts\run_web.bat
```

桌面 GUI（可选）：

```powershell
python main.py
```

## Linux 服务器部署（长远）

开发与测试在 Windows 完成后，上 Linux 服务器只需：

```bash
# 服务器上
git clone https://github.com/Vincentssssssss/Rei-Cai.git
cd Rei-Cai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # 填入与本地相同的配置
python3 check_llm.py
python3 web_main.py    # 或配合 systemd / Docker 后台运行
```

生产环境建议：
- 使用 `web_main.py`（与 Windows 开发相同入口）
- 前面加 Nginx 反向代理
- 用 systemd 或 Docker 保持进程常驻
- `data/knowledge/` 和 `data/index/` 持久化挂载

## 本地 Linux 桌面运行

### 环境要求

- Linux
- Python 3.10+
- Tk 图形库（Ubuntu/Debian：`sudo apt install python3-tk`）

### 安装与运行

```bash
pip install -r requirements.txt
python main.py          # 桌面 GUI
python web_main.py      # 或 Web 版本（浏览器访问 http://localhost:8000）
```

## 使用流程

1. 启动程序，进入首页
2. 点击「管理入口」，上传资料文件
3. 点击「重建索引」，等待索引完成
4. 返回首页，进入「用户入口」开始对话

## 可选：接入大模型（阿里云百炼）

> DashScope（灵积）控制台已下线，请使用 **大模型服务平台百炼**：https://bailian.console.aliyun.com/

1. 在百炼控制台创建 API Key
2. 在百炼控制台复制 **OpenAI 兼容 Base URL**（格式如 `https://llm-xxxxx.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`）
3. 配置 `.env`：

```bash
cp .env.example .env
```

```bash
OPENAI_API_KEY=你的百炼API密钥
OPENAI_BASE_URL=https://llm-xxxxx.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=openai/qwen-plus
```

或设置环境变量：

```bash
export OPENAI_API_KEY="你的百炼API密钥"
export OPENAI_BASE_URL="https://llm-xxxxx.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
export OPENAI_MODEL="openai/qwen-plus"
python3 web_main.py
```

> 注意：`BAILIAN_WORKSPACE_ID` 需为 `llm-` 开头的地址前缀，**不是**控制台里的纯数字 ID。推荐直接填写完整的 `OPENAI_BASE_URL`。

`OPENAI_MODEL` 中的 `openai/` 前缀会自动去除。

未完整配置时，系统会基于资料检索直接整理相关片段作为回答。首页和管理端会显示当前大模型配置状态。

## 项目结构

```
├── main.py                 # 桌面 GUI（Windows/macOS/Linux）
├── web_main.py             # Web 入口（全平台，推荐）
├── check_llm.py            # API 连接诊断
├── requirements.txt
├── scripts/
│   ├── run_web.sh          # Linux/macOS 一键启动
│   ├── run_web.bat         # Windows 一键启动
│   └── setup_env.sh
├── .devcontainer/          # Codespaces 配置
├── data/
│   ├── knowledge/          # 上传的资料文件
│   └── index/              # 检索索引
└── src/
    ├── config.py
    ├── chat/engine.py      # 对话引擎
    ├── knowledge/          # 资料加载与索引
    ├── gui/                # 桌面图形界面
    └── web/                # Web 界面
```

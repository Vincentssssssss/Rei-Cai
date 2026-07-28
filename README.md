# Rei-Cai

基于资料学习的智能对话机器人，支持 **Linux 桌面 GUI** 与 **GitHub Codespaces Web 展示**。

## 功能

- **双入口界面**：首页提供「用户入口」与「管理入口」，无需登录认证
- **资料管理**：支持上传 `.txt`、`.md`、`.pdf` 文件
- **知识索引**：自动分块并建立 TF-IDF 检索索引
- **智能问答**：根据已上传资料检索相关内容并生成回答
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
cp .env.example .env
```

或在仓库 **Settings → Secrets and variables → Codespaces** 中添加：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL` = `https://api.openai.com/v1`
- `OPENAI_MODEL` = `openai/qwen-plus`

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

## 可选：接入大模型

复制示例配置并填入你的 API Key：

```bash
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY
python web_main.py   # Codespaces
# 或 python main.py  # 本地桌面
```

或直接设置环境变量：

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_MODEL="openai/qwen-plus"
python web_main.py
```

`OPENAI_MODEL` 中的 `openai/` 前缀会自动去除。也兼容 `STRIX_LLM` 环境变量。

未配置 API Key 时，系统会基于资料检索直接整理相关片段作为回答。

## 项目结构

```
├── main.py                 # 桌面 GUI 入口
├── web_main.py             # Web 入口（Codespaces）
├── requirements.txt
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

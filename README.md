# Rei-Cai

基于资料学习的智能对话机器人，适用于 Linux 桌面环境。

## 功能

- **双入口界面**：首页提供「用户入口」与「管理入口」，无需登录认证
- **资料管理**：支持上传 `.txt`、`.md`、`.pdf` 文件
- **知识索引**：自动分块并建立 TF-IDF 检索索引
- **智能问答**：根据已上传资料检索相关内容并生成回答
- **可选 LLM**：配置 `OPENAI_API_KEY` 后可调用 OpenAI 兼容 API 生成更自然的回答

## 环境要求

- Linux
- Python 3.10+
- Tk 图形库（Ubuntu/Debian：`sudo apt install python3-tk`）

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 使用流程

1. 启动程序，进入首页
2. 点击「管理入口」，上传资料文件
3. 点击「重建索引」，等待索引完成
4. 返回首页，进入「用户入口」开始对话

## 可选：接入大模型（阿里云 DashScope / Qwen）

复制示例配置并填入你的 API Key：

```bash
cp .env.example .env
# 编辑 .env 填入 OPENAI_API_KEY
python main.py
```

或直接设置环境变量：

```bash
export OPENAI_API_KEY="your-api-key"
export STRIX_LLM="openai/qwen-plus"
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
python main.py
```

也支持 `OPENAI_MODEL` 作为模型名环境变量。`STRIX_LLM` 中的 `openai/` 前缀会自动去除。

未配置 API Key 时，系统会基于资料检索直接整理相关片段作为回答。

## 项目结构

```
├── main.py                 # 程序入口
├── requirements.txt
├── data/
│   ├── knowledge/          # 上传的资料文件
│   └── index/              # 检索索引
└── src/
    ├── config.py
    ├── chat/engine.py      # 对话引擎
    ├── knowledge/          # 资料加载与索引
    └── gui/                # 图形界面
```

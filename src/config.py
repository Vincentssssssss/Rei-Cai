import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
INDEX_DIR = DATA_DIR / "index"

KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
TOP_K = 4

DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
OPENAI_OFFICIAL_BASE_URL = "https://api.openai.com/v1"


def _normalize_model_name(raw: str) -> str:
    """Strip framework prefixes like openai/ from model identifiers."""
    if "/" in raw:
        return raw.split("/", 1)[1]
    return raw


def get_llm_settings() -> dict[str, str]:
    api_key = os.getenv("OPENAI_API_KEY", "")
    model_raw = os.getenv("OPENAI_MODEL") or os.getenv("STRIX_LLM", "openai/qwen-plus")
    model = _normalize_model_name(model_raw)

    base_url = os.getenv("OPENAI_BASE_URL", "").strip().rstrip("/")
    if not base_url:
        base_url = DASHSCOPE_BASE_URL if "qwen" in model.lower() else OPENAI_OFFICIAL_BASE_URL

    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
    }


def get_llm_hint(settings: dict[str, str] | None = None) -> str | None:
    settings = settings or get_llm_settings()
    model = settings["model"].lower()
    base_url = settings["base_url"].lower()

    if "qwen" in model and "openai.com" in base_url:
        return (
            "qwen 模型请使用阿里云 DashScope 地址："
            f"{DASHSCOPE_BASE_URL}"
        )
    return None


def get_llm_status() -> dict[str, str | bool | None]:
    settings = get_llm_settings()
    return {
        "configured": bool(settings["api_key"]),
        "base_url": settings["base_url"],
        "model": settings["model"],
        "hint": get_llm_hint(settings),
    }

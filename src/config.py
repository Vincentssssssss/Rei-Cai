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


def _normalize_model_name(raw: str) -> str:
    """Strip framework prefixes like openai/ from model identifiers."""
    if "/" in raw:
        return raw.split("/", 1)[1]
    return raw


def get_llm_settings() -> dict[str, str]:
    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1").rstrip("/")
    model = os.getenv("STRIX_LLM") or os.getenv("OPENAI_MODEL", "qwen-plus")
    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": _normalize_model_name(model),
    }

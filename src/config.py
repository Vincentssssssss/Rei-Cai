import os
from pathlib import Path

from dotenv import load_dotenv

import src.http_client  # noqa: F401 - configure SSL certificates early

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

OPENAI_OFFICIAL_BASE_URL = "https://api.openai.com/v1"
LEGACY_DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 阿里云百炼地域 -> MaaS 域名后缀
BAILIAN_REGION_HOSTS = {
    "cn-beijing": "cn-beijing.maas.aliyuncs.com",
    "ap-southeast-1": "ap-southeast-1.maas.aliyuncs.com",
    "cn-hongkong": "cn-hongkong.maas.aliyuncs.com",
    "ap-northeast-1": "ap-northeast-1.maas.aliyuncs.com",
    "eu-central-1": "eu-central-1.maas.aliyuncs.com",
}


def _normalize_model_name(raw: str) -> str:
    if "/" in raw:
        return raw.split("/", 1)[1]
    return raw


def _is_qwen_model(model: str) -> bool:
    return "qwen" in model.lower()


def build_bailian_base_url(workspace_id: str, region: str = "cn-beijing") -> str:
    host = BAILIAN_REGION_HOSTS.get(region, BAILIAN_REGION_HOSTS["cn-beijing"])
    return f"https://{workspace_id}.{host}/compatible-mode/v1"


def _resolve_api_key() -> str:
    return os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY", "")


def _resolve_base_url(model: str) -> str:
    workspace_id = os.getenv("BAILIAN_WORKSPACE_ID") or os.getenv("WORKSPACE_ID", "").strip()
    region = os.getenv("BAILIAN_REGION", "cn-beijing").strip()

    base_url = os.getenv("OPENAI_BASE_URL", "").strip().rstrip("/")
    if base_url:
        if "{WorkspaceId}" in base_url and workspace_id:
            return base_url.replace("{WorkspaceId}", workspace_id)
        return base_url

    if _is_qwen_model(model) and workspace_id:
        return build_bailian_base_url(workspace_id, region)

    if _is_qwen_model(model):
        return ""

    return OPENAI_OFFICIAL_BASE_URL


def get_llm_settings() -> dict[str, str]:
    model_raw = os.getenv("OPENAI_MODEL") or os.getenv("STRIX_LLM", "openai/qwen-plus")
    model = _normalize_model_name(model_raw)
    return {
        "api_key": _resolve_api_key(),
        "base_url": _resolve_base_url(model),
        "model": model,
        "workspace_id": os.getenv("BAILIAN_WORKSPACE_ID") or os.getenv("WORKSPACE_ID", ""),
        "region": os.getenv("BAILIAN_REGION", "cn-beijing"),
    }


def get_llm_hint(settings: dict[str, str] | None = None) -> str | None:
    settings = settings or get_llm_settings()
    model = settings["model"].lower()
    base_url = settings.get("base_url", "").lower()
    workspace_id = settings.get("workspace_id", "")

    if not _is_qwen_model(model):
        if "openai.com" not in base_url and base_url:
            return None
        return None

    if "openai.com" in base_url:
        return "qwen 模型请使用阿里云百炼地址，不要使用 api.openai.com。"

    if "dashscope.aliyuncs.com" in base_url:
        return (
            "DashScope 控制台已迁移至百炼平台。请设置 BAILIAN_WORKSPACE_ID，"
            "并将 OPENAI_BASE_URL 改为 "
            "https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
        )

    if not base_url and not workspace_id:
        return (
            "请在百炼控制台获取业务空间 ID，并在 .env 中设置 BAILIAN_WORKSPACE_ID。"
            "控制台：https://bailian.console.aliyun.com/"
        )

    if "{workspaceid}" in base_url:
        return "OPENAI_BASE_URL 中的 {WorkspaceId} 需要替换为真实的 BAILIAN_WORKSPACE_ID。"

    return None


def get_llm_status() -> dict[str, str | bool | None]:
    settings = get_llm_settings()
    return {
        "configured": bool(settings["api_key"] and settings["base_url"]),
        "api_key_set": bool(settings["api_key"]),
        "base_url": settings["base_url"] or "未配置",
        "model": settings["model"],
        "workspace_id": settings.get("workspace_id") or None,
        "hint": get_llm_hint(settings),
    }

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
INDEX_DIR = DATA_DIR / "index"

KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
TOP_K = 4

# Optional: set OPENAI_API_KEY and OPENAI_BASE_URL for smarter replies
LLM_API_KEY = ""
LLM_BASE_URL = "https://api.openai.com/v1"
LLM_MODEL = "gpt-4o-mini"

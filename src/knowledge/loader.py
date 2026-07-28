import re
from pathlib import Path

from pypdf import PdfReader

from src.config import CHUNK_OVERLAP, CHUNK_SIZE, SUPPORTED_EXTENSIONS


def load_text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    raise ValueError(f"Unsupported file type: {suffix}")


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def load_documents(knowledge_dir: Path) -> list[dict]:
    documents: list[dict] = []
    for path in sorted(knowledge_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        try:
            content = load_text_from_file(path)
            for index, chunk in enumerate(split_text(content)):
                documents.append(
                    {
                        "source": path.name,
                        "chunk_id": index,
                        "text": chunk,
                    }
                )
        except Exception as exc:
            documents.append(
                {
                    "source": path.name,
                    "chunk_id": 0,
                    "text": f"[无法读取文件: {exc}]",
                }
            )
    return documents

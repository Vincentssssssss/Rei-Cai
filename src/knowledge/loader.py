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
        pages = [f"[[PAGE:{idx + 1}]] {page.extract_text() or ''}" for idx, page in enumerate(reader.pages)]
        return "\n".join(pages)
    raise ValueError(f"Unsupported file type: {suffix}")


def infer_doc_version(source_name: str) -> str:
    lowered = source_name.lower()
    version_match = re.search(r"v\d{4,8}|v[a-z]", lowered)
    if version_match:
        return version_match.group(0)
    if "2022" in lowered:
        return "2022"
    return "unknown"


def infer_section_hint(text: str) -> str:
    lowered = text.lower()
    if "meal" in lowered or "breakfast" in lowered:
        return "Meal"
    if "hotel" in lowered:
        return "Hotel"
    if "airfare" in lowered or "flight" in lowered:
        return "Airfare"
    if "visa" in lowered:
        return "Visa"
    if "contact" in lowered or "email" in lowered:
        return "Contact"
    return "General"


def infer_page_hint(text: str) -> int | None:
    marker = re.search(r"\[\[PAGE:(\d+)\]\]", text)
    if marker:
        return int(marker.group(1))
    page_match = re.search(r"\bpage\s+(\d+)\b", text, re.IGNORECASE)
    if page_match:
        return int(page_match.group(1))
    return None


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
                        "doc_version": infer_doc_version(path.name),
                        "section_hint": infer_section_hint(chunk),
                        "page_hint": infer_page_hint(chunk),
                    }
                )
        except Exception as exc:
            documents.append(
                {
                    "source": path.name,
                    "chunk_id": 0,
                    "text": f"[无法读取文件: {exc}]",
                    "doc_version": infer_doc_version(path.name),
                    "section_hint": "General",
                    "page_hint": None,
                }
            )
    return documents

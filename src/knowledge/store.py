import json
import pickle
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import INDEX_DIR, KNOWLEDGE_DIR, TOP_K
from src.knowledge.loader import load_documents


class KnowledgeStore:
    def __init__(self) -> None:
        self.documents: list[dict] = []
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None
        self.meta_path = INDEX_DIR / "meta.json"
        self.vector_path = INDEX_DIR / "vectors.pkl"
        self._load_index()

    def _load_index(self) -> None:
        if not self.meta_path.exists() or not self.vector_path.exists():
            return
        self.documents = json.loads(self.meta_path.read_text(encoding="utf-8"))
        with self.vector_path.open("rb") as handle:
            payload = pickle.load(handle)
        self.vectorizer = payload["vectorizer"]
        self.matrix = payload["matrix"]

    def rebuild(self) -> int:
        self.documents = load_documents(KNOWLEDGE_DIR)
        if not self.documents:
            self.vectorizer = None
            self.matrix = None
            if self.meta_path.exists():
                self.meta_path.unlink()
            if self.vector_path.exists():
                self.vector_path.unlink()
            return 0

        texts = [doc["text"] for doc in self.documents]
        self.vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
        self.matrix = self.vectorizer.fit_transform(texts)

        self.meta_path.write_text(json.dumps(self.documents, ensure_ascii=False, indent=2), encoding="utf-8")
        with self.vector_path.open("wb") as handle:
            pickle.dump({"vectorizer": self.vectorizer, "matrix": self.matrix}, handle)
        return len(self.documents)

    def search(self, query: str, top_k: int = TOP_K) -> list[dict]:
        if not self.documents or self.vectorizer is None or self.matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)

        results: list[dict] = []
        for idx, score in ranked[:top_k]:
            if score <= 0:
                continue
            item = dict(self.documents[idx])
            item["score"] = float(score)
            results.append(item)
        return results

    def list_sources(self) -> list[dict]:
        sources: dict[str, dict] = {}
        for path in sorted(KNOWLEDGE_DIR.iterdir()):
            if not path.is_file():
                continue
            sources[path.name] = {
                "name": path.name,
                "size_kb": round(path.stat().st_size / 1024, 1),
                "chunks": 0,
            }
        for doc in self.documents:
            name = doc["source"]
            if name in sources:
                sources[name]["chunks"] += 1
        return list(sources.values())

    def delete_source(self, filename: str) -> None:
        target = KNOWLEDGE_DIR / filename
        if target.exists():
            target.unlink()
        self.rebuild()

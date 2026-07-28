import requests

from src.config import get_llm_settings
from src.knowledge.store import KnowledgeStore


class ChatEngine:
    def __init__(self, store: KnowledgeStore) -> None:
        self.store = store
        settings = get_llm_settings()
        self.api_key = settings["api_key"]
        self.base_url = settings["base_url"]
        self.model = settings["model"]

    def answer(self, question: str) -> tuple[str, list[dict]]:
        hits = self.store.search(question)
        if not hits:
            return (
                "知识库中暂无相关内容。请先在管理端上传资料并重建索引。",
                [],
            )

        if self.api_key:
            try:
                return self._answer_with_llm(question, hits), hits
            except Exception as exc:
                return self._answer_with_retrieval(question, hits) + f"\n\n（LLM 调用失败，已改用资料检索：{exc}）", hits

        return self._answer_with_retrieval(question, hits), hits

    def _answer_with_retrieval(self, question: str, hits: list[dict]) -> str:
        lines = ["根据已学习的资料，整理如下：", ""]
        for index, hit in enumerate(hits, start=1):
            lines.append(f"{index}. 来源：{hit['source']}")
            lines.append(hit["text"])
            lines.append("")
        lines.append("如需更精确的答案，可在环境变量中配置 OPENAI_API_KEY。")
        return "\n".join(lines)

    def _answer_with_llm(self, question: str, hits: list[dict]) -> str:
        context_blocks = []
        for hit in hits:
            context_blocks.append(f"[{hit['source']}]\n{hit['text']}")
        context = "\n\n".join(context_blocks)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是基于用户资料回答问题的助手。只根据提供的资料作答，"
                        "资料中没有的信息请明确说明不知道，不要编造。"
                    ),
                },
                {
                    "role": "user",
                    "content": f"资料：\n{context}\n\n问题：{question}",
                },
            ],
            "temperature": 0.2,
        }
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

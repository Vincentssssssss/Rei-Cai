import requests
from requests.exceptions import RequestException

from src.chat.citations import build_citations
from src.config import DASHSCOPE_BASE_URL, get_llm_hint, get_llm_settings
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
                hint = self._format_llm_error(exc)
                return (
                    self._answer_with_retrieval(question, hits)
                    + f"\n\n（LLM 调用失败，已改用资料检索）\n{hint}",
                    hits,
                )

        return self._answer_with_retrieval(question, hits), hits

    def _answer_with_retrieval(self, question: str, hits: list[dict]) -> str:
        top = hits[0]["text"].strip()
        if len(top) > 320:
            top = top[:320].rstrip() + "..."
        lines = [f"根据已学习的资料：{top}", ""]
        lines.append("详细引用请见下方「引用」区域。")
        if not self.api_key:
            lines.append(
                "如需更自然的回答，请配置环境变量：OPENAI_API_KEY、OPENAI_BASE_URL、OPENAI_MODEL。"
            )
        return "\n".join(lines)

    def _format_llm_error(self, exc: Exception) -> str:
        messages = [f"原因：{exc.__class__.__name__}"]

        config_hint = get_llm_hint(
            {
                "api_key": self.api_key,
                "base_url": self.base_url,
                "model": self.model,
            }
        )
        if config_hint:
            messages.append(config_hint)

        error_text = str(exc)
        if "SSL" in error_text or "SSLError" in error_text:
            messages.append(
                "SSL 连接失败，常见于国内网络访问 api.openai.com。"
                f"若使用 qwen 模型，请将 OPENAI_BASE_URL 设为 {DASHSCOPE_BASE_URL}"
            )
        elif isinstance(exc, RequestException) and not config_hint:
            messages.append("请检查 OPENAI_BASE_URL 与 API Key 是否正确。")

        return "\n".join(messages)

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
                        "回答时在相关语句后标注引用来源，使用 [文件名] 格式。"
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

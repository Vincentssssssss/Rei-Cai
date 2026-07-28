import requests
from requests.exceptions import RequestException

from src.config import get_llm_hint, get_llm_settings
from src.http_client import create_http_session
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

        if self.api_key and self.base_url:
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
                "如需更自然的回答，请配置 OPENAI_API_KEY 与 BAILIAN_WORKSPACE_ID。"
            )
        elif not self.base_url:
            lines.append(
                "已配置 API Key，但缺少百炼 API 地址。请设置 OPENAI_BASE_URL。"
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
        if "CERTIFICATE_VERIFY_FAILED" in error_text:
            messages.append(
                "SSL 证书验证失败。请执行：pip install certifi && python3 scripts/check_llm.py"
            )
        elif "UNEXPECTED_EOF_WHILE_READING" in error_text or "SSLEOFError" in error_text:
            messages.append(
                "SSL 连接中断，常见于网络不稳定或代理/VPN 干扰。"
                "请关闭代理后重试，或执行 python3 scripts/check_llm.py 诊断。"
            )
        elif "SSL" in error_text or "SSLError" in error_text:
            messages.append(
                "SSL 连接失败。请执行：pip install certifi && python3 scripts/check_llm.py"
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
        session = create_http_session()
        response = session.post(
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

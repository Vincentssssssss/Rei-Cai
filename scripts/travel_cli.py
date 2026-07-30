#!/usr/bin/env python3
from src.knowledge.store import KnowledgeStore
from src.travel_agent.runtime.service import TravelAssistantService


def format_reply(payload: dict) -> str:
    lines = [payload.get("answer", ""), "", "引用："]
    citations = payload.get("citations", [])
    if citations:
        for index, item in enumerate(citations, start=1):
            source = item.get("source", "unknown")
            version = item.get("doc_version", "unknown")
            section = item.get("section_hint", "General")
            page = item.get("page_hint")
            page_suffix = f", page {page}" if page else ""
            excerpt = str(item.get("excerpt", ""))[:160]
            lines.append(f"{index}. [{source}] ({version}, {section}{page_suffix}) {excerpt}")
    else:
        lines.append("无")

    if payload.get("handoff_required"):
        lines.append("")
        lines.append(f"转人工原因：{payload.get('handoff_reason') or 'unknown'}")
    return "\n".join(lines)


def main() -> None:
    store = KnowledgeStore()
    if not store.documents:
        store.rebuild()
    service = TravelAssistantService(store=store)

    print("Travel Assistant CLI（输入 quit 退出）")
    while True:
        question = input("你：").strip()
        if question.lower() in {"quit", "exit"}:
            break
        if not question:
            continue
        result = service.ask(question)
        print(format_reply(result))


if __name__ == "__main__":
    main()

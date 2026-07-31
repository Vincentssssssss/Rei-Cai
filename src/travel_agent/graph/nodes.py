from src.chat.citations import build_citations
from src.config import get_llm_settings, get_travel_agent_system_prompt
from src.http_client import create_http_session

ESCALATION_EMAILS = "su.vincent@bcg.com / Zhang.Zhen@bcg.com"
ESCALATION_MESSAGE = f"如需人工支持，请联系 {ESCALATION_EMAILS}。"

BLOCKED_PATTERNS = ("直接审批", "帮我审批", "修改政策", "承诺特批", "代我预订", "替我预订")

INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "policy": ("政策", "报销", "标准", "规定", "早餐", "住宿"),
    "hotel": ("酒店", "协议价", "sourcing", "住宿"),
    "process": ("如何", "流程", "申请", "取消", "操作"),
    "contact": ("联系人", "联系谁", "邮箱", "负责人"),
    "visa": ("签证", "出入境"),
}


def _expand_query(question: str) -> str:
    expanded = question
    replacements = {
        "早餐": " breakfast meal ",
        "报销": " reimburse reimbursement ",
        "酒店": " hotel accommodation ",
        "政策": " policy ",
        "签证": " visa ",
        "联系人": " contact email ",
    }
    for zh, en in replacements.items():
        if zh in expanded:
            expanded = f"{expanded} {en}"
    return expanded


def classify_intent(state: dict) -> dict:
    question = state["question"].lower()
    intent = "other"
    for name, keywords in INTENT_KEYWORDS.items():
        if any(keyword.lower() in question for keyword in keywords):
            intent = name
            break
    return {"intent": intent, "region": "Greater China"}


def retrieve_knowledge(state: dict, store) -> dict:
    question = state["question"]
    hits = store.search(question)
    if not hits:
        hits = store.search(_expand_query(question))
    return {"retrieved_chunks": hits, "citations": build_citations(hits)}


def policy_guard(state: dict) -> dict:
    question = state["question"]
    if any(pattern in question for pattern in BLOCKED_PATTERNS):
        return {
            "handoff_required": True,
            "handoff_reason": "out_of_scope",
            "answer": (
                "结论：该请求超出 Agent 权限范围，无法直接处理。\n"
                "依据：Agent 不执行审批、预订或政策修改操作。\n"
                f"下一步：{ESCALATION_MESSAGE}"
            ),
        }
    if not state.get("retrieved_chunks"):
        return {
            "handoff_required": True,
            "handoff_reason": "no_evidence",
            "answer": (
                "结论：当前知识库无法确认该问题。\n"
                "依据：未检索到可用的官方政策依据。\n"
                f"下一步：{ESCALATION_MESSAGE}"
            ),
        }
    return {"handoff_required": False, "handoff_reason": None}


def _contains_breakfast_not_cover(hits: list[dict]) -> bool:
    for item in hits:
        snippet = str(item.get("text", "")).lower()
        if "not cover" in snippet and "breakfast" in snippet:
            return True
    return False


def _extract_policy_conclusion(hits: list[dict]) -> tuple[str | None, str]:
    if not hits:
        return None, ""

    top_text = str(hits[0].get("text", "")).strip()
    text = top_text.lower()
    deny_markers = (
        "not cover",
        "not reimbursable",
        "not allowed",
        "不可报销",
        "不报销",
        "不允许",
    )
    allow_markers = (
        "reimbursed",
        "reimbursable",
        "allowed",
        "可报销",
        "可以报销",
        "允许",
    )

    if any(marker in text for marker in deny_markers):
        return "deny", top_text
    if any(marker in text for marker in allow_markers):
        return "allow", top_text
    return None, top_text


def _answer_with_llm(question: str, hits: list[dict]) -> str | None:
    settings = get_llm_settings()
    api_key = settings.get("api_key", "")
    base_url = settings.get("base_url", "")
    model = settings.get("model", "")
    if not api_key or not base_url or not model:
        return None

    context_blocks: list[str] = []
    for item in hits:
        context_blocks.append(
            (
                f"[source={item.get('source')}, version={item.get('doc_version')}, "
                f"section={item.get('section_hint')}, page={item.get('page_hint')}]\n"
                f"{item.get('text', '')}"
            )
        )
    context = "\n\n".join(context_blocks)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": get_travel_agent_system_prompt()},
            {
                "role": "user",
                "content": (
                    f"问题：{question}\n\n"
                    f"资料片段（仅可基于这些资料回答）：\n{context}\n\n"
                    "如果资料不足，请明确说无法确认并建议联系人工支持邮箱。"
                ),
            },
        ],
        "temperature": 0.1,
    }

    try:
        session = create_http_session()
        response = session.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].strip()
        return content or None
    except Exception:
        return None


def compose_answer(state: dict) -> dict:
    if state.get("handoff_required"):
        return {}

    hits = state.get("retrieved_chunks", [])
    intent = state.get("intent", "other")
    llm_answer = _answer_with_llm(state["question"], hits)
    if llm_answer:
        return {"answer": llm_answer, "confidence": 0.8}

    if _contains_breakfast_not_cover(hits):
        return {
            "answer": (
                "结论：不可以，酒店早餐不可报销。\n"
                "依据：政策中 Meal 条款将 Breakfast 列为 Not cover（不报销）。\n"
                f"下一步：如为特殊场景，请先按例外审批流程申请；需要人工确认请联系 {ESCALATION_EMAILS}。"
            ),
            "confidence": 0.95,
        }

    if intent == "policy":
        conclusion, evidence = _extract_policy_conclusion(hits)
        if conclusion == "deny":
            return {
                "answer": (
                    "结论：不可以（或不在报销范围）。\n"
                    f"依据：命中政策片段为「{evidence[:180]}」。\n"
                    f"下一步：如你认为属于例外场景，请按审批流程申请，并联系 {ESCALATION_EMAILS}。"
                ),
                "confidence": 0.88,
            }
        if conclusion == "allow":
            return {
                "answer": (
                    "结论：可以，但需按政策条件和单据要求执行。\n"
                    f"依据：命中政策片段为「{evidence[:180]}」。\n"
                    f"下一步：请按标准流程提交；如涉及边界或例外，请联系 {ESCALATION_EMAILS}。"
                ),
                "confidence": 0.82,
            }
        return {
            "answer": (
                "结论：当前无法给出精确政策结论。\n"
                f"依据：已检索到相关片段，但不足以直接回答你的问题（示例片段：{evidence[:160]}）。\n"
                f"下一步：请联系人工支持进一步确认：{ESCALATION_EMAILS}。"
            ),
            "confidence": 0.2,
        }

    if intent == "contact":
        return {
            "answer": (
                "结论：请联系 Travel/Finance 支持邮箱。\n"
                f"依据：该问题属于人工协助类咨询。\n下一步：{ESCALATION_MESSAGE}"
            ),
            "confidence": 0.8,
        }

    return {
        "answer": (
            "结论：当前无法给出精确答复。\n"
            "依据：已检索到相关资料，但未形成可直接执行的明确结论。\n"
            f"下一步：请联系人工支持确认：{ESCALATION_EMAILS}。"
        ),
        "confidence": 0.2,
    }


def handoff_decider(state: dict) -> dict:
    if state.get("handoff_required"):
        return {}

    confidence = float(state.get("confidence", 0))
    if confidence < 0.4:
        return {
            "handoff_required": True,
            "handoff_reason": "low_confidence",
            "answer": (
                f"{state.get('answer', '')}\n"
                f"由于当前证据置信度不足，建议转人工进一步确认。{ESCALATION_MESSAGE}"
            ),
        }
    return {"handoff_required": False, "handoff_reason": None}


def collect_feedback(_: dict) -> dict:
    return {"satisfaction_prompted": True}

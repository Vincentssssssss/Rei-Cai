from src.chat.citations import build_citations

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


def compose_answer(state: dict) -> dict:
    if state.get("handoff_required"):
        return {}

    hits = state.get("retrieved_chunks", [])
    intent = state.get("intent", "other")

    if _contains_breakfast_not_cover(hits):
        return {
            "answer": (
                "结论：不可以，酒店早餐不可报销。\n"
                "依据：政策中 Meal 条款将 Breakfast 列为 Not cover（不报销）。\n"
                "下一步：如为特殊场景，请先按例外审批流程申请；无法确认时转人工支持。"
            ),
            "confidence": 0.95,
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
            "结论：请以以下引用的官方资料为准。\n"
            "依据：已检索到相关政策片段，详见引用。\n"
            "下一步：如涉及特殊审批，请先走审批流程并联系人工支持确认。"
        ),
        "confidence": 0.65,
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

from typing import Literal, TypedDict

Intent = Literal["policy", "hotel", "process", "contact", "visa", "other"]


class TravelAgentState(TypedDict, total=False):
    question: str
    region: str
    intent: Intent
    retrieved_chunks: list[dict]
    answer: str
    citations: list[dict]
    confidence: float
    handoff_required: bool
    handoff_reason: str | None
    satisfaction_prompted: bool

from src.travel_agent.runtime.service import TravelAssistantService


class EmptyStore:
    documents: list[dict] = []

    def search(self, query: str, top_k: int = 4):
        return []


def test_unknown_question_must_escalate():
    service = TravelAssistantService(store=EmptyStore())
    result = service.ask("帮我直接审批超标酒店")
    assert result["handoff_required"] is True
    assert result["handoff_reason"] == "out_of_scope"
    assert "人工支持" in result["answer"]
    assert "su.vincent@bcg.com" in result["answer"]

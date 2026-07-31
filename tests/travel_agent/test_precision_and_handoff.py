from src.travel_agent.runtime.service import TravelAssistantService


class AmbiguousPolicyStore:
    documents: list[dict] = []

    def search(self, query: str, top_k: int = 4):
        return [
            {
                "source": "GC_TE_Policy_v202212.pdf",
                "text": "Please submit your expense claims properly and in a timely manner.",
                "doc_version": "v202212",
                "section_hint": "General",
                "page_hint": 5,
                "score": 0.6,
            }
        ]


def test_ambiguous_policy_question_forces_handoff_with_contacts():
    service = TravelAssistantService(store=AmbiguousPolicyStore())
    result = service.ask("酒店早餐餐费到底怎么报销")
    assert result["handoff_required"] is True
    assert "无法给出精确政策结论" in result["answer"]
    assert "su.vincent@bcg.com" in result["answer"]
    assert "Zhang.Zhen@bcg.com" in result["answer"]

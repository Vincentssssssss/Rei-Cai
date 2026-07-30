from src.travel_agent.runtime.service import TravelAssistantService


class StubStore:
    documents: list[dict] = []

    def search(self, query: str, top_k: int = 4):
        return [
            {
                "source": "GC_TE_Policy_v202212.pdf",
                "text": "Meal Not cover Breakfast",
                "doc_version": "v202212",
                "section_hint": "Meal",
                "page_hint": 6,
                "score": 0.92,
            },
            {
                "source": "Travel___Expense_Traning_vF.pdf",
                "text": "Not cover Breakfast",
                "doc_version": "vF",
                "section_hint": "Meal",
                "page_hint": 10,
                "score": 0.88,
            },
        ]


def test_breakfast_reimbursement_is_denied_with_citations():
    service = TravelAssistantService(store=StubStore())
    result = service.ask("酒店早餐可以报销餐费吗")
    assert "不可以" in result["answer"]
    assert len(result["citations"]) >= 2
    assert result["handoff_required"] is False
    assert result["intent"] == "policy"

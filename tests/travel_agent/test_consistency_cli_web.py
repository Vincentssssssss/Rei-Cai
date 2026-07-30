from scripts.travel_cli import format_reply
from src.travel_agent.runtime.service import TravelAssistantService


class BreakfastStore:
    documents: list[dict] = []

    def search(self, query: str, top_k: int = 4):
        return [
            {
                "source": "GC_TE_Policy_v202212.pdf",
                "text": "Not cover Breakfast",
                "doc_version": "v202212",
                "section_hint": "Meal",
                "page_hint": 6,
                "score": 0.9,
            },
        ]


def test_cli_and_service_share_same_conclusion():
    service = TravelAssistantService(store=BreakfastStore())
    payload = service.ask("酒店早餐可以报销餐费吗")
    rendered = format_reply(payload)
    assert "不可以" in payload["answer"]
    assert "不可以" in rendered

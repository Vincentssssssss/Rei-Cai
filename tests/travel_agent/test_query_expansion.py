from src.travel_agent.graph.nodes import retrieve_knowledge


class ExpansionStore:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def search(self, query: str, top_k: int = 4):
        self.queries.append(query)
        if len(self.queries) == 1:
            return []
        return [
            {
                "source": "GC_TE_Policy_v202212.pdf",
                "text": "Meal Not cover Breakfast",
                "doc_version": "v202212",
                "section_hint": "Meal",
                "page_hint": 6,
                "score": 0.91,
            }
        ]


def test_retrieve_knowledge_uses_expanded_query_on_empty_first_hit():
    store = ExpansionStore()
    result = retrieve_knowledge({"question": "酒店早餐可以报销餐费吗"}, store)
    assert len(store.queries) == 2
    assert "breakfast" in store.queries[1].lower()
    assert result["retrieved_chunks"]

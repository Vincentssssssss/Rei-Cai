from src.travel_agent.graph.builder import build_graph


class TravelAssistantService:
    def __init__(self, store) -> None:
        self._graph = build_graph(store)

    def ask(self, question: str) -> dict:
        result = self._graph.invoke({"question": question})
        return {
            "answer": result.get("answer", ""),
            "citations": result.get("citations", []),
            "handoff_required": bool(result.get("handoff_required", False)),
            "handoff_reason": result.get("handoff_reason"),
            "intent": result.get("intent", "other"),
            "satisfaction_prompted": bool(result.get("satisfaction_prompted", False)),
        }

from langgraph.graph import END, START, StateGraph

from src.travel_agent.graph.nodes import (
    classify_intent,
    collect_feedback,
    compose_answer,
    handoff_decider,
    policy_guard,
    retrieve_knowledge,
)
from src.travel_agent.graph.state import TravelAgentState


def build_graph(store):
    graph = StateGraph(TravelAgentState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_knowledge", lambda state: retrieve_knowledge(state, store))
    graph.add_node("policy_guard", policy_guard)
    graph.add_node("compose_answer", compose_answer)
    graph.add_node("handoff_decider", handoff_decider)
    graph.add_node("collect_feedback", collect_feedback)

    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "retrieve_knowledge")
    graph.add_edge("retrieve_knowledge", "policy_guard")
    graph.add_edge("policy_guard", "compose_answer")
    graph.add_edge("compose_answer", "handoff_decider")
    graph.add_edge("handoff_decider", "collect_feedback")
    graph.add_edge("collect_feedback", END)
    return graph.compile()

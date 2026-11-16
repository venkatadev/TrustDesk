"""Wires the nodes into the per-question LangGraph."""

from langgraph.graph import END, START, StateGraph

from trustdesk.agent.nodes import draft, match_library, retrieve, route, verify
from trustdesk.agent.state import QuestionState

MAX_ATTEMPTS = 2  # the first draft plus one retry, as in the design


def after_library(state: QuestionState) -> str:
    return "route" if state.reused else "retrieve"


def after_retrieve(state: QuestionState) -> str:
    return "draft" if state.chunks else "route"  # nothing found: skip drafting


def verdict(state: QuestionState) -> str:
    if state.verified:
        return "pass"
    return "retry" if state.attempts < MAX_ATTEMPTS else "fail"


def build_graph():
    g = StateGraph(QuestionState)
    g.add_node("library", match_library)
    g.add_node("retrieve", retrieve)
    g.add_node("draft", draft)
    g.add_node("verify", verify)
    g.add_node("route", route)

    g.add_edge(START, "library")
    g.add_conditional_edges("library", after_library, {"route": "route", "retrieve": "retrieve"})
    g.add_conditional_edges("retrieve", after_retrieve, {"draft": "draft", "route": "route"})
    g.add_edge("draft", "verify")
    g.add_conditional_edges("verify", verdict, {"pass": "route", "retry": "draft", "fail": "route"})
    g.add_edge("route", END)
    return g.compile()

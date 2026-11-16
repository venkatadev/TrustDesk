"""The document-level LangGraph: fans every question out in parallel, then gathers them in order."""

from collections import Counter

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from trustdesk.agent.graph import build_graph
from trustdesk.agent.state import DocumentState, QuestionState


def build_document_graph(question_graph=None):
    """`question_graph` can be injected (tests, later a checkpointed one); default is the real one."""
    question_graph = question_graph or build_graph()

    def fan_out(state: DocumentState):
        sends = [Send("answer_question", {"index": i, "question": q}) for i, q in enumerate(state.questions)]
        return sends or ["finalize"]  # nothing to answer: go straight to the end

    def answer_question(task: dict) -> dict:
        """Run one question. A crash is recorded on that question instead of losing the whole document."""
        try:
            final = QuestionState(**question_graph.invoke({"question": task["question"]}))
        except Exception as exc:  # noqa: BLE001 - isolating any failure per question is the point
            final = QuestionState(question=task["question"], status="needs_human", error=f"{type(exc).__name__}: {exc}")
        return {"answered": [(task["index"], final)]}

    def finalize(state: DocumentState) -> dict:
        results = [q for _, q in sorted(state.answered, key=lambda pair: pair[0])]
        return {"results": results, "counts": dict(Counter(q.status for q in results))}

    g = StateGraph(DocumentState)
    g.add_node("answer_question", answer_question)
    g.add_node("finalize", finalize)
    g.add_conditional_edges(START, fan_out)
    g.add_edge("answer_question", "finalize")
    g.add_edge("finalize", END)
    return g.compile()

"""The one entry point other modules (API, worker) use to answer a questionnaire."""

from trustdesk.agent.document_graph import build_document_graph
from trustdesk.agent.state import DocumentState


def run_questionnaire(questions: list[str]) -> DocumentState:
    """Answer every question; results come back in the same order, with per-status counts."""
    return DocumentState(**build_document_graph().invoke({"questions": questions}))

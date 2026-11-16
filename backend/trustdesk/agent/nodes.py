"""Nodes of the per-question graph. Each node reads the state and returns ONLY what changed."""

from trustdesk.agent.state import QuestionState
from trustdesk.guardrails.grounding import is_grounded
from trustdesk.knowledge.answer_library import SAMPLE_LIBRARY
from trustdesk.knowledge.store import get_policy_store
from trustdesk.llm.drafting import get_drafter


def match_library(state: QuestionState) -> dict:
    """Reuse an approved answer if the library has one for this exact question."""
    answer = SAMPLE_LIBRARY.find(state.question)
    if answer is None:
        return {"reused": False}
    return {"reused": True, "draft": answer}


def retrieve(state: QuestionState) -> dict:
    """Search the current policy store for chunks relevant to the question."""
    return {"chunks": [chunk.text for chunk in get_policy_store().search(state.question)]}


def draft(state: QuestionState) -> dict:
    """Write an answer from the retrieved chunks. On a retry, the rejected draft is passed back."""
    previous = state.draft if state.attempts > 0 else None
    text = get_drafter()(state.question, state.chunks, previous)
    return {"draft": text, "attempts": state.attempts + 1}


def verify(state: QuestionState) -> dict:
    """Accept the draft only if it is grounded in the retrieved chunks."""
    return {"verified": is_grounded(state.draft, state.chunks)}


def route(state: QuestionState) -> dict:
    """Decide the final outcome: ready, needs_human, or no_evidence."""
    if state.reused or state.verified:
        return {"status": "ready"}
    if not state.chunks:
        return {"status": "no_evidence"}
    return {"status": "needs_human"}

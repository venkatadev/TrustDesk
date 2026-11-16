"""Nodes of the per-question graph. Each node reads the state and returns ONLY what changed."""

from trustdesk.agent.state import QuestionState


def match_library(state: QuestionState) -> dict:
    """Stub: pretend the answer library has no match for this question."""
    return {"reused": False}


def retrieve(state: QuestionState) -> dict:
    """Stub: pretend the policy search found one relevant chunk."""
    return {"chunks": ["Backups are encrypted at rest with AES-256 using AWS-managed keys."]}


def draft(state: QuestionState) -> dict:
    """Stub: pretend the model wrote an answer using only the retrieved chunks."""
    return {"draft": f"Draft based on: {state.chunks[0]}", "attempts": state.attempts + 1}


def verify(state: QuestionState) -> dict:
    """Stub: reject the first draft and accept the second, so the retry loop is visible."""
    return {"verified": state.attempts >= 2}


def route(state: QuestionState) -> dict:
    """Decide the final outcome: ready, needs_human, or no_evidence."""
    if state.reused or state.verified:
        return {"status": "ready"}
    if not state.chunks:
        return {"status": "no_evidence"}
    return {"status": "needs_human"}

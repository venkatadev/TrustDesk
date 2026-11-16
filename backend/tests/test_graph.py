"""Tests for the wired per-question graph: the paths a question can take."""

import pytest

from trustdesk.agent import graph as graph_module
from trustdesk.agent.graph import MAX_ATTEMPTS, build_graph, verdict
from trustdesk.agent.state import QuestionState

QUESTION = {"question": "Do you encrypt backups?"}


def run(app) -> QuestionState:
    """Run the graph and rebuild the full state, so unwritten fields get their defaults."""
    return QuestionState(**app.invoke(QUESTION))


def test_default_path_retries_once_then_ready():
    final = build_graph().invoke(QUESTION)
    assert final["status"] == "ready"
    assert final["verified"] is True
    assert final["attempts"] == 2  # first draft rejected, second accepted


def test_library_hit_skips_retrieve_and_draft(monkeypatch):
    monkeypatch.setattr(graph_module, "match_library", lambda s: {"reused": True})
    final = run(build_graph())
    assert final.status == "ready"
    assert final.attempts == 0  # no drafting happened
    assert final.chunks == []  # no retrieval happened
    assert final.draft is None


def test_nothing_retrieved_ends_as_no_evidence(monkeypatch):
    monkeypatch.setattr(graph_module, "retrieve", lambda s: {"chunks": []})
    final = run(build_graph())
    assert final.status == "no_evidence"
    assert final.attempts == 0  # drafting was skipped, never guessed


def test_verification_always_failing_ends_as_needs_human(monkeypatch):
    monkeypatch.setattr(graph_module, "verify", lambda s: {"verified": False})
    final = build_graph().invoke(QUESTION)
    assert final["status"] == "needs_human"
    assert final["attempts"] == MAX_ATTEMPTS  # stopped after the allowed retry, no endless loop


@pytest.mark.parametrize(
    ("verified", "attempts", "expected"),
    [
        (True, 1, "pass"),
        (False, 1, "retry"),
        (False, MAX_ATTEMPTS, "fail"),
    ],
)
def test_verdict(verified, attempts, expected):
    state = QuestionState(question="q", verified=verified, attempts=attempts)
    assert verdict(state) == expected

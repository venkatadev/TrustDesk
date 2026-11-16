"""Tests for individual nodes and the state model."""

import pytest
from pydantic import ValidationError

from trustdesk.agent.nodes import draft, match_library, route, verify
from trustdesk.agent.state import QuestionState


def test_new_state_starts_pending_and_empty():
    s = QuestionState(question="q")
    assert s.status == "pending"
    assert s.chunks == []
    assert s.attempts == 0


def test_state_rejects_unknown_status():
    with pytest.raises(ValidationError):
        QuestionState(question="q", status="bogus")


def test_states_do_not_share_chunk_lists():
    a, b = QuestionState(question="a"), QuestionState(question="b")
    a.chunks.append("x")
    assert b.chunks == []


def test_node_returns_update_without_changing_state():
    s = QuestionState(question="q")
    assert match_library(s) == {"reused": False}
    assert s.reused is False


def test_draft_uses_first_chunk_and_counts_attempt():
    s = QuestionState(question="q", chunks=["policy text"], attempts=1)
    update = draft(s)
    assert "policy text" in update["draft"]
    assert update["attempts"] == 2


def test_verify_rejects_first_draft_accepts_second():
    assert verify(QuestionState(question="q", attempts=1)) == {"verified": False}
    assert verify(QuestionState(question="q", attempts=2)) == {"verified": True}


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        (QuestionState(question="q", reused=True), "ready"),
        (QuestionState(question="q", chunks=["c"], verified=True), "ready"),
        (QuestionState(question="q", chunks=["c"], verified=False), "needs_human"),
        (QuestionState(question="q"), "no_evidence"),
    ],
)
def test_route(state, expected):
    assert route(state)["status"] == expected

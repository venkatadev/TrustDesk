"""Tests for the approved-answer library and the match_library node that uses it."""

from trustdesk.agent.nodes import match_library
from trustdesk.agent.state import QuestionState
from trustdesk.knowledge.answer_library import SAMPLE_LIBRARY, AnswerLibrary, normalize


def test_normalize_ignores_case_punctuation_and_spacing():
    assert normalize("  Do you  have SSO? ") == "do you have sso"


def test_find_matches_despite_formatting_differences():
    lib = AnswerLibrary({"Do you have SSO?": "Yes, via SAML."})
    assert lib.find("do you have  sso") == "Yes, via SAML."


def test_find_returns_none_when_unknown():
    assert AnswerLibrary().find("anything") is None


def test_add_makes_a_question_findable():
    lib = AnswerLibrary()
    lib.add("Is data encrypted?", "Yes.")
    assert lib.find("is data encrypted") == "Yes."


def test_match_library_hit_sets_reused_and_uses_the_approved_answer():
    question = "Do you have a vendor risk management program?"
    update = match_library(QuestionState(question=question))
    assert update == {"reused": True, "draft": SAMPLE_LIBRARY.find(question)}


def test_match_library_miss_reuses_nothing():
    assert match_library(QuestionState(question="Do you encrypt backups?")) == {"reused": False}

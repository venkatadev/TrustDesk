"""Tests for keyword search and the retrieve node that uses it."""

from trustdesk.agent.nodes import retrieve
from trustdesk.agent.state import QuestionState
from trustdesk.knowledge.sample_policies import SAMPLE_POLICIES
from trustdesk.knowledge.search import search

BACKUPS, MFA, INCIDENT = SAMPLE_POLICIES


def test_finds_the_chunk_about_the_topic():
    assert search("Do you encrypt backups?", SAMPLE_POLICIES) == [BACKUPS]
    assert search("Is MFA enforced?", SAMPLE_POLICIES) == [MFA]


def test_unrelated_question_finds_nothing():
    assert search("Do you hold a pet policy?", SAMPLE_POLICIES) == []


def test_question_filler_words_do_not_cause_matches():
    assert search("Do you? What? How?", SAMPLE_POLICIES) == []


def test_best_match_first_and_top_k_limits_results():
    chunks = ["backups exist", "backups are encrypted", "unrelated text"]
    assert search("encrypted backups", chunks) == ["backups are encrypted", "backups exist"]
    assert search("encrypted backups", chunks, top_k=1) == ["backups are encrypted"]


def test_retrieve_node_returns_chunks_for_the_question():
    update = retrieve(QuestionState(question="Do you have an incident plan?"))
    assert update == {"chunks": [INCIDENT]}

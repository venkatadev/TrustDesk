"""Tests for the word-overlap grounding check."""

from trustdesk.guardrails.grounding import is_grounded

CHUNK = "Backups are encrypted at rest with AES-256 using AWS-managed keys."


def test_draft_copied_from_chunk_is_grounded():
    assert is_grounded(CHUNK, [CHUNK])


def test_paraphrase_with_same_facts_is_grounded():
    assert is_grounded("Backups are encrypted using AES-256 keys.", [CHUNK])


def test_invented_claim_is_not_grounded():
    assert not is_grounded("We hold SOC 2 Type II and ISO 27001 certifications.", [CHUNK])


def test_missing_draft_or_chunks_is_not_grounded():
    assert not is_grounded(None, [CHUNK])
    assert not is_grounded("", [CHUNK])
    assert not is_grounded(CHUNK, [])


def test_support_can_come_from_any_chunk():
    chunks = ["Backups are encrypted at rest.", "Keys are AWS-managed."]
    assert is_grounded("Backups are encrypted with AWS-managed keys.", chunks)

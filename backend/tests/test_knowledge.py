"""Tests for chunking, policy loading, the store, and using a real store through the agent."""

import pytest

from trustdesk.agent.run import run_questionnaire
from trustdesk.knowledge.chunking import Chunk, chunk_text
from trustdesk.knowledge.ingest import load_policies
from trustdesk.knowledge.store import PolicyStore, get_policy_store, set_policy_store

# ---- chunking ---------------------------------------------------------------------------------


def test_one_chunk_per_paragraph():
    assert chunk_text("First paragraph.\n\nSecond paragraph.") == ["First paragraph.", "Second paragraph."]


def test_blank_text_gives_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("  \n\n \n") == []


def test_heading_stays_with_the_paragraph_after_it():
    text = "# Backups\n\nBackups are encrypted.\n\n# Access\n\nMFA is required."
    assert chunk_text(text) == ["# Backups\nBackups are encrypted.", "# Access\nMFA is required."]


def test_trailing_heading_is_not_lost():
    assert chunk_text("Some text.\n\n# Empty section") == ["Some text.", "# Empty section"]


def test_long_paragraph_is_split_at_sentence_ends():
    sentences = [f"Sentence number {i} is here." for i in range(10)]
    chunks = chunk_text(" ".join(sentences), max_chars=80)
    assert len(chunks) > 1
    assert all(len(c) <= 80 for c in chunks)
    assert " ".join(chunks) == " ".join(sentences)  # nothing lost, nothing duplicated


def test_one_enormous_sentence_is_cut_at_the_limit():
    chunks = chunk_text("x" * 250, max_chars=100)
    assert [len(c) for c in chunks] == [100, 100, 50]


# ---- loading ----------------------------------------------------------------------------------


def test_load_policies_reads_txt_and_md_recursively_and_ignores_others(tmp_path):
    (tmp_path / "backup.md").write_text("# Backups\n\nBackups are encrypted.", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "access.txt").write_text("MFA is required.", encoding="utf-8")
    (tmp_path / "logo.png").write_bytes(b"\x89PNG")
    chunks = load_policies(tmp_path)
    assert chunks == [
        Chunk("backup.md", "# Backups\nBackups are encrypted."),
        Chunk("sub/access.txt", "MFA is required."),
    ]


def test_load_policies_fails_clearly_for_a_missing_folder(tmp_path):
    with pytest.raises(FileNotFoundError, match="policy folder not found"):
        load_policies(tmp_path / "nope")


# ---- store ------------------------------------------------------------------------------------


def test_store_search_returns_chunks_with_their_source():
    store = PolicyStore([Chunk("a.md", "Backups are encrypted."), Chunk("b.md", "MFA is required.")])
    assert store.search("Is MFA required?") == [Chunk("b.md", "MFA is required.")]


def test_default_store_is_the_sample_policies():
    assert {c.source for c in get_policy_store().chunks} == {"sample"}


def test_agent_answers_from_the_store_that_was_set(tmp_path):
    (tmp_path / "dr.md").write_text("Disaster recovery drills run every quarter.", encoding="utf-8")
    set_policy_store(PolicyStore.from_directory(tmp_path))
    final = run_questionnaire(["Do you run disaster recovery drills?", "Do you encrypt backups?"])
    first, second = final.results
    assert first.status == "ready" and "quarter" in first.draft
    assert second.status == "no_evidence"  # the sample backup policy is no longer in play

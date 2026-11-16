"""The policy store the agent searches, and the one place that decides which store is in use."""

from pathlib import Path

from trustdesk.knowledge.chunking import Chunk
from trustdesk.knowledge.ingest import load_policies
from trustdesk.knowledge.sample_policies import SAMPLE_POLICIES
from trustdesk.knowledge.search import search


class PolicyStore:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = list(chunks)

    @classmethod
    def from_directory(cls, directory: Path | str) -> "PolicyStore":
        return cls(load_policies(directory))

    def search(self, question: str, top_k: int = 3) -> list[Chunk]:
        return search(question, self.chunks, top_k, text=lambda chunk: chunk.text)


_current = PolicyStore([Chunk("sample", text) for text in SAMPLE_POLICIES])  # default until configured


def get_policy_store() -> PolicyStore:
    return _current


def set_policy_store(store: PolicyStore) -> None:
    """Choose the store the agent uses. Call once at startup (CLI, worker, API)."""
    global _current
    _current = store

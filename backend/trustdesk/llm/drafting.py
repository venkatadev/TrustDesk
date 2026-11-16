"""Drafters: how the agent's `draft` step turns (question, chunks) into answer text."""

from collections.abc import Callable

from trustdesk.llm.client import LLMClient
from trustdesk.llm.prompts import DRAFT_SYSTEM, build_draft_prompt

# (question, chunks, previous_rejected_draft_or_None) -> answer text
Drafter = Callable[[str, list[str], str | None], str]


def extractive_drafter(question: str, chunks: list[str], previous: str | None) -> str:
    """No model: answer with the best-matching chunk, word for word. Always grounded; never fluent."""
    return chunks[0]


def llm_drafter(client: LLMClient) -> Drafter:
    def draft(question: str, chunks: list[str], previous: str | None) -> str:
        return client.complete(DRAFT_SYSTEM, build_draft_prompt(question, chunks, previous))

    return draft


_current: Drafter = extractive_drafter  # default until a model is configured


def get_drafter() -> Drafter:
    return _current


def set_drafter(drafter: Drafter) -> None:
    """Choose how answers are drafted. Call once at startup (CLI, worker, API)."""
    global _current
    _current = drafter

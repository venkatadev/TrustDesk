"""Keyword search over policy chunks. A first, simple stand-in for hybrid (vector + keyword) retrieval."""

from collections.abc import Callable
from typing import TypeVar

from trustdesk.guardrails.grounding import STOPWORDS, content_words

T = TypeVar("T")

# Words that fill questions ("Do you ...?") but say nothing about the topic being asked.
_IGNORED = STOPWORDS | {"do", "does", "you", "your", "what", "how", "which", "can", "will"}


def search(
    question: str,
    items: list[T],
    top_k: int = 3,
    text: Callable[[T], str] = lambda item: item,  # type: ignore[assignment,return-value]
) -> list[T]:
    """Return up to `top_k` items sharing topic words with the question, best match first.

    `text` says how to get the searchable text out of an item (default: the item is the text).
    Items sharing no topic word are dropped, so an unrelated question returns [] (no evidence).
    """
    wanted = content_words(question) - _IGNORED
    scored = [(len(wanted & content_words(text(item))), item) for item in items]
    hits = [(score, item) for score, item in scored if score > 0]
    hits.sort(key=lambda pair: pair[0], reverse=True)  # stable: ties keep original order
    return [item for _, item in hits[:top_k]]

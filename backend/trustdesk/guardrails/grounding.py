"""Grounding check: is every claim in a draft backed by the retrieved policy text?

This is a cheap, deterministic first gate (word overlap). A model-based check can be added later
behind the same `is_grounded` signature.
"""

import re

GROUNDING_THRESHOLD = 0.8  # share of the draft's content words that must appear in the chunks

STOPWORDS = frozenset(
    "a an and are as at be by for from has have in is it of on or that the this to was we were with".split()
)


def content_words(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9][a-z0-9-]*", text.lower())
    return {w for w in words if w not in STOPWORDS}


def is_grounded(draft: str | None, chunks: list[str]) -> bool:
    """True if enough of the draft's content words are found in the chunks."""
    if not draft or not chunks:
        return False
    words = content_words(draft)
    if not words:
        return False
    support = set().union(*(content_words(c) for c in chunks))
    return len(words & support) / len(words) >= GROUNDING_THRESHOLD

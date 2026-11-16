"""Split policy text into chunks small enough to retrieve and cite individually."""

import re
from dataclasses import dataclass

MAX_CHARS = 800


@dataclass(frozen=True)
class Chunk:
    source: str  # which policy file the text came from (needed later for citations)
    text: str


def _split_long(paragraph: str, max_chars: int) -> list[str]:
    """Break an over-long paragraph at sentence ends; a single huge sentence is cut hard."""
    if len(paragraph) <= max_chars:
        return [paragraph]
    pieces, current = [], ""
    for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
        while len(sentence) > max_chars:  # no sentence end in sight: cut at the limit
            if current:
                pieces.append(current)
                current = ""
            pieces.append(sentence[:max_chars])
            sentence = sentence[max_chars:]
        if current and len(current) + 1 + len(sentence) > max_chars:
            pieces.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        pieces.append(current)
    return pieces


def chunk_text(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    """One chunk per paragraph. A markdown heading line is kept with the paragraph that follows it."""
    chunks, heading = [], ""
    for paragraph in (p.strip() for p in re.split(r"\n\s*\n", text)):
        if not paragraph:
            continue
        if paragraph.startswith("#") and "\n" not in paragraph:
            heading = f"{heading}\n{paragraph}".strip()  # stacked headings stay together
            continue
        chunks.extend(_split_long(f"{heading}\n{paragraph}".strip(), max_chars))
        heading = ""
    if heading:  # a trailing heading with nothing under it
        chunks.append(heading)
    return chunks

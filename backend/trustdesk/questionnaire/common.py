"""Pieces shared by every questionnaire file format."""

from dataclasses import dataclass

ANSWER_HEADER = "Answer"  # header used when a questionnaire has no answer column yet


@dataclass(frozen=True)
class Question:
    row: int  # 1-based row in the file (the header row is row 1), so answers can be written back
    text: str


def find_columns(header: list[str]) -> tuple[int, int | None]:
    """Return (question column, answer column or None), as 0-based indexes.

    The question column is the first header containing "question" (else the first column).
    The answer column is the first other header containing "answer" or "response".
    """
    lowered = [h.strip().lower() for h in header]
    question = next((i for i, h in enumerate(lowered) if "question" in h), 0)
    answer = next(
        (i for i, h in enumerate(lowered) if i != question and ("answer" in h or "response" in h)),
        None,
    )
    return question, answer

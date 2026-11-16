"""State models for the per-question graph and the document graph."""

import operator
from typing import Annotated, Literal

from pydantic import BaseModel


class QuestionState(BaseModel):
    """State that travels with ONE question through the per-question graph."""

    question: str  # the question text from the questionnaire
    reused: bool = False  # True if an approved library answer was found
    chunks: list[str] = []  # policy text found by retrieve (the only text the draft may use)
    draft: str | None = None  # the drafted answer (citations come later)
    verified: bool = False  # did the verifier accept the draft?
    attempts: int = 0  # how many drafts so far (design allows one retry)
    status: Literal["pending", "ready", "needs_human", "no_evidence"] = "pending"
    error: str | None = None  # set if processing this question crashed; it then needs a human


class DocumentState(BaseModel):
    """State that travels with ONE whole questionnaire through the document graph."""

    questions: list[str]  # every question text, in questionnaire order
    # Questions run in parallel, so each finished one is appended here with its original index.
    answered: Annotated[list[tuple[int, QuestionState]], operator.add] = []
    results: list[QuestionState] = []  # `answered` put back in questionnaire order
    counts: dict[str, int] = {}  # how many questions ended in each status

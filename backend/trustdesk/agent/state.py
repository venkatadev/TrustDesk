"""State that travels with ONE question through the per-question graph."""

from typing import Literal

from pydantic import BaseModel


class QuestionState(BaseModel):
    question: str  # the question text from the questionnaire
    reused: bool = False  # True if an approved library answer was found
    chunks: list[str] = []  # policy text found by retrieve (the only text the draft may use)
    draft: str | None = None  # the drafted answer (citations come later)
    verified: bool = False  # did the verifier accept the draft?
    attempts: int = 0  # how many drafts so far (design allows one retry)
    status: Literal["pending", "ready", "needs_human", "no_evidence"] = "pending"

"""Library of previously approved answers. A question that matches one is answered without drafting."""

import re


def normalize(question: str) -> str:
    """Lowercase, drop punctuation, collapse spaces: so 'Do you  have SSO?' matches 'do you have sso'."""
    return " ".join(re.findall(r"[a-z0-9-]+", question.lower()))


class AnswerLibrary:
    def __init__(self, answers: dict[str, str] | None = None):
        self._answers = {normalize(q): a for q, a in (answers or {}).items()}

    def add(self, question: str, answer: str) -> None:
        self._answers[normalize(question)] = answer

    def find(self, question: str) -> str | None:
        return self._answers.get(normalize(question))


SAMPLE_LIBRARY = AnswerLibrary(
    {"Do you have a vendor risk management program?": "Yes. Vendors are risk-assessed before onboarding and annually."}
)

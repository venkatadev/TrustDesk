"""Read questions from, and write answers into, a CSV questionnaire."""

import csv
from pathlib import Path

from trustdesk.questionnaire.common import ANSWER_HEADER, Question, find_columns

# utf-8-sig: Excel saves CSVs with a byte-order mark; this reads it away and writes it back so
# Excel still opens the output correctly.
_ENCODING = "utf-8-sig"


def _load(path: Path) -> list[list[str]]:
    with open(path, newline="", encoding=_ENCODING) as f:
        return list(csv.reader(f))


def read_csv(path: Path) -> list[Question]:
    rows = _load(path)
    if not rows:
        return []
    column, _ = find_columns(rows[0])
    return [
        Question(row=number, text=row[column].strip())
        for number, row in enumerate(rows[1:], start=2)
        if len(row) > column and row[column].strip()
    ]


def write_csv(source: Path, dest: Path, answers: dict[int, str]) -> None:
    """Copy `source` to `dest`, filling the answer column. Every other cell is left untouched."""
    rows = _load(source)
    if not rows:
        raise ValueError(f"{source} is empty")
    _, answer_column = find_columns(rows[0])
    if answer_column is None:
        answer_column = len(rows[0])
        rows[0].append(ANSWER_HEADER)
    for row in rows:
        row.extend([""] * (answer_column + 1 - len(row)))  # short rows get padded, answered or not
    for number, answer in answers.items():
        if not 2 <= number <= len(rows):
            raise ValueError(f"row {number} is not a question row in {source}")
        rows[number - 1][answer_column] = answer
    with open(dest, "w", newline="", encoding=_ENCODING) as f:
        csv.writer(f).writerows(rows)

"""Read questions from, and write answers into, an xlsx questionnaire (first sheet)."""

from pathlib import Path

from openpyxl import load_workbook

from trustdesk.questionnaire.common import ANSWER_HEADER, Question, find_columns


def _header(sheet) -> list[str]:
    return [str(cell.value or "") for cell in sheet[1]]


def read_xlsx(path: Path) -> list[Question]:
    workbook = load_workbook(path, read_only=True)
    try:
        sheet = workbook.worksheets[0]
        rows = list(sheet.iter_rows(values_only=True))
    finally:
        workbook.close()
    if not rows:
        return []
    column, _ = find_columns([str(v or "") for v in rows[0]])
    questions = []
    for number, row in enumerate(rows[1:], start=2):
        value = row[column] if len(row) > column else None
        if value is not None and str(value).strip():
            questions.append(Question(row=number, text=str(value).strip()))
    return questions


def write_xlsx(source: Path, dest: Path, answers: dict[int, str]) -> None:
    """Copy `source` to `dest`, filling the answer column. Existing cells and formatting are kept."""
    workbook = load_workbook(source)
    sheet = workbook.worksheets[0]
    header = _header(sheet)
    _, answer_column = find_columns(header)
    if answer_column is None:
        answer_column = len(header)
        sheet.cell(row=1, column=answer_column + 1, value=ANSWER_HEADER)
    for number, answer in answers.items():
        if not 2 <= number <= sheet.max_row:
            raise ValueError(f"row {number} is not a question row in {source}")
        sheet.cell(row=number, column=answer_column + 1, value=answer)
    workbook.save(dest)

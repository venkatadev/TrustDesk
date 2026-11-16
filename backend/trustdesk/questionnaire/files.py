"""One interface over all questionnaire formats; the file extension picks the format."""

from pathlib import Path

from trustdesk.questionnaire.common import Question
from trustdesk.questionnaire.csv_format import read_csv, write_csv
from trustdesk.questionnaire.xlsx_format import read_xlsx, write_xlsx

_FORMATS = {
    ".csv": (read_csv, write_csv),
    ".xlsx": (read_xlsx, write_xlsx),
}


class UnsupportedFormat(ValueError):
    pass


def _format(path: Path):
    try:
        return _FORMATS[path.suffix.lower()]
    except KeyError:
        supported = ", ".join(sorted(_FORMATS))
        raise UnsupportedFormat(f"cannot handle '{path.suffix}' files (supported: {supported})") from None


def read_questions(path: Path | str) -> list[Question]:
    path = Path(path)
    return _format(path)[0](path)


def write_answers(source: Path | str, dest: Path | str, answers: dict[int, str]) -> None:
    """`answers` maps a Question.row to its answer text. `dest` must use the same format as `source`."""
    source, dest = Path(source), Path(dest)
    if source.suffix.lower() != dest.suffix.lower():
        raise UnsupportedFormat("source and destination must be the same file type")
    _format(source)[1](source, dest, answers)

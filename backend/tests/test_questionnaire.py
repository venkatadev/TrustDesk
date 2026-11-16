"""Tests for questionnaire reading/writing (csv, xlsx) and the whole-file workflow."""

import csv

import pytest
from openpyxl import Workbook, load_workbook

from trustdesk.questionnaire.common import Question, find_columns
from trustdesk.questionnaire.files import UnsupportedFormat, read_questions, write_answers
from trustdesk.questionnaire.process import answer_file


def make_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows(rows)
    return path


def make_xlsx(path, rows):
    wb = Workbook()
    for row in rows:
        wb.active.append(row)
    wb.save(path)
    return path


def read_csv_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


# ---- column detection -------------------------------------------------------------------------


def test_find_columns_by_header_words():
    assert find_columns(["ID", "Security Question", "Vendor Response"]) == (1, 2)


def test_find_columns_falls_back_to_first_column_and_no_answer_column():
    assert find_columns(["Item", "Notes"]) == (0, None)


def test_find_columns_on_empty_header():
    assert find_columns([]) == (0, None)


# ---- reading ----------------------------------------------------------------------------------


@pytest.mark.parametrize("maker, name", [(make_csv, "q.csv"), (make_xlsx, "q.xlsx")])
def test_read_questions_skips_blank_rows_and_records_row_numbers(tmp_path, maker, name):
    path = maker(tmp_path / name, [["ID", "Question"], [1, "Do you encrypt backups?"], [2, ""], [3, "Is MFA enforced?"]])
    assert read_questions(path) == [
        Question(row=2, text="Do you encrypt backups?"),
        Question(row=4, text="Is MFA enforced?"),
    ]


def test_read_csv_handles_excel_byte_order_mark(tmp_path):
    path = make_csv(tmp_path / "q.csv", [["Question"], ["Do you encrypt backups?"]])
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")  # the fixture really has a BOM
    assert read_questions(path)[0].text == "Do you encrypt backups?"


def test_read_empty_files_gives_no_questions(tmp_path):
    (tmp_path / "empty.csv").write_text("")
    assert read_questions(tmp_path / "empty.csv") == []


def test_unsupported_extension_is_rejected(tmp_path):
    with pytest.raises(UnsupportedFormat, match=r"\.docx"):
        read_questions(tmp_path / "q.docx")


# ---- writing ----------------------------------------------------------------------------------


def test_write_csv_fills_existing_answer_column_and_keeps_the_rest(tmp_path):
    src = make_csv(tmp_path / "q.csv", [["ID", "Question", "Answer"], ["1", "Q one?", ""], ["2", "Q two?", "old"]])
    dest = tmp_path / "out.csv"
    write_answers(src, dest, {2: "New answer"})
    assert read_csv_rows(dest) == [["ID", "Question", "Answer"], ["1", "Q one?", "New answer"], ["2", "Q two?", "old"]]
    assert read_csv_rows(src)[1][2] == ""  # the source file is never modified


def test_write_csv_adds_an_answer_column_when_missing_and_pads_short_rows(tmp_path):
    src = make_csv(tmp_path / "q.csv", [["Question", "Notes"], ["Q one?"]])
    dest = tmp_path / "out.csv"
    write_answers(src, dest, {2: "A"})
    assert read_csv_rows(dest) == [["Question", "Notes", "Answer"], ["Q one?", "", "A"]]


def test_write_xlsx_adds_answer_column_and_keeps_existing_cells(tmp_path):
    src = make_xlsx(tmp_path / "q.xlsx", [["ID", "Question"], [1, "Q one?"], [2, "Q two?"]])
    dest = tmp_path / "out.xlsx"
    write_answers(src, dest, {3: "Answer two"})
    sheet = load_workbook(dest).worksheets[0]
    assert [c.value for c in sheet[1]] == ["ID", "Question", "Answer"]
    assert [c.value for c in sheet[2]] == [1, "Q one?", None]
    assert [c.value for c in sheet[3]] == [2, "Q two?", "Answer two"]


@pytest.mark.parametrize("row", [1, 99])
def test_writing_to_a_header_or_missing_row_is_an_error(tmp_path, row):
    src = make_csv(tmp_path / "q.csv", [["Question"], ["Q?"]])
    with pytest.raises(ValueError, match="not a question row"):
        write_answers(src, tmp_path / "out.csv", {row: "x"})


def test_source_and_destination_must_be_the_same_type(tmp_path):
    src = make_csv(tmp_path / "q.csv", [["Question"], ["Q?"]])
    with pytest.raises(UnsupportedFormat):
        write_answers(src, tmp_path / "out.xlsx", {})


# ---- whole workflow ---------------------------------------------------------------------------


def test_answer_file_end_to_end_csv(tmp_path):
    src = make_csv(
        tmp_path / "q.csv",
        [["Question"], ["Do you encrypt backups?"], ["Do you hold a pet policy?"], ["Is MFA enforced?"]],
    )
    dest = tmp_path / "out.csv"
    state = answer_file(src, dest)
    rows = read_csv_rows(dest)
    assert rows[0] == ["Question", "Answer"]
    assert "AES-256" in rows[1][1]  # drafted from the backup policy
    assert rows[2][1] == ""  # no evidence: left blank for a human
    assert "MFA" in rows[3][1]
    assert state.counts == {"ready": 2, "no_evidence": 1}


def test_answer_file_end_to_end_xlsx(tmp_path):
    src = make_xlsx(tmp_path / "q.xlsx", [["Question", "Answer"], ["Do you encrypt backups?", None]])
    dest = tmp_path / "out.xlsx"
    answer_file(src, dest)
    assert "AES-256" in load_workbook(dest).worksheets[0]["B2"].value

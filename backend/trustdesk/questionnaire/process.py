"""Whole-file workflow: questionnaire in, agent runs, answered questionnaire out."""

from pathlib import Path

from trustdesk.agent.run import run_questionnaire
from trustdesk.agent.state import DocumentState
from trustdesk.questionnaire.files import read_questions, write_answers


def answer_file(source: Path | str, dest: Path | str) -> DocumentState:
    """Write drafts for every question that is `ready`. Others are left blank for a human to handle.

    Returns the full agent result so the caller can see which questions need attention.
    """
    questions = read_questions(source)
    state = run_questionnaire([q.text for q in questions])
    answers = {
        question.row: result.draft
        for question, result in zip(questions, state.results, strict=True)
        if result.status == "ready" and result.draft
    }
    write_answers(source, dest, answers)
    return state

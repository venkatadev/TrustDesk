"""Tests for the document-level graph and run_questionnaire: parallel, ordered, failure-isolated."""

import time

from trustdesk.agent import graph as graph_module
from trustdesk.agent.document_graph import build_document_graph
from trustdesk.agent.run import run_questionnaire
from trustdesk.agent.state import DocumentState


class FakeQuestionGraph:
    """Stands in for the per-question graph; `behave` decides what each question does."""

    def __init__(self, behave):
        self.behave = behave

    def invoke(self, payload):
        return self.behave(payload["question"])


def test_one_result_per_question_in_order():
    questions = ["Do you encrypt backups?", "Do you have an incident plan?", "Is MFA enforced?"]
    final = run_questionnaire(questions)
    assert [r.question for r in final.results] == questions
    assert all(r.status == "ready" for r in final.results)


def test_empty_questionnaire_gives_no_results():
    final = run_questionnaire([])
    assert final.results == []
    assert final.counts == {}


def test_each_question_takes_its_own_path(monkeypatch):
    def retrieve(state):  # only the backup question has policy evidence
        found = "backups" in state.question
        return {"chunks": ["Backups are encrypted at rest with AES-256."] if found else []}

    monkeypatch.setattr(graph_module, "retrieve", retrieve)
    final = run_questionnaire(["Do you encrypt backups?", "Do you hold a pet policy?"])
    assert [r.status for r in final.results] == ["ready", "no_evidence"]
    assert final.counts == {"ready": 1, "no_evidence": 1}


def test_library_answer_is_reused_without_drafting():
    final = run_questionnaire(["Do you have a vendor risk management program?"])
    result = final.results[0]
    assert result.status == "ready"
    assert result.attempts == 0
    assert result.draft is not None


def test_order_is_kept_even_when_questions_finish_out_of_order():
    def behave(question):  # earlier questions take longer, so they finish last
        time.sleep(0.05 * (3 - int(question)))
        return {"question": question, "status": "ready"}

    app = build_document_graph(FakeQuestionGraph(behave))
    final = DocumentState(**app.invoke({"questions": ["0", "1", "2"]}))
    assert [r.question for r in final.results] == ["0", "1", "2"]


def test_a_crashing_question_is_recorded_and_does_not_lose_the_others():
    def behave(question):
        if question == "boom":
            raise RuntimeError("model unavailable")
        return {"question": question, "status": "ready"}

    app = build_document_graph(FakeQuestionGraph(behave))
    final = DocumentState(**app.invoke({"questions": ["a", "boom", "c"]}))
    assert [r.status for r in final.results] == ["ready", "needs_human", "ready"]
    assert final.results[1].error == "RuntimeError: model unavailable"
    assert final.counts == {"ready": 2, "needs_human": 1}

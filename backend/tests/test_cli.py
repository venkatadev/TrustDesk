"""Tests for the command-line entry point."""

import csv

from trustdesk.questionnaire.__main__ import main


def write_questionnaire(path, questions):
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([["Question"], *[[q] for q in questions]])


def test_cli_answers_a_file_and_reports_what_needs_attention(tmp_path, capsys):
    policies = tmp_path / "policies"
    policies.mkdir()
    (policies / "dr.md").write_text("Disaster recovery drills run every quarter.", encoding="utf-8")
    src, dest = tmp_path / "q.csv", tmp_path / "out.csv"
    write_questionnaire(src, ["Do you run disaster recovery drills?", "Do you hold a pet policy?"])

    code = main([str(src), str(dest), "--policies", str(policies)])

    out = capsys.readouterr().out
    assert code == 0
    assert "1 no_evidence, 1 ready" in out
    assert "needs attention (no_evidence): Do you hold a pet policy?" in out
    with open(dest, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    assert "quarter" in rows[1][1]
    assert rows[2][1] == ""


def test_cli_with_a_model_id_drafts_through_bedrock(tmp_path, monkeypatch, capsys):
    created = {}

    class FakeBedrock:
        def __init__(self, model_id, region=None):
            created.update(model_id=model_id, region=region)

        def complete(self, system, prompt):
            return "Disaster recovery drills run every quarter."

    monkeypatch.setattr("trustdesk.questionnaire.__main__.BedrockClient", FakeBedrock)
    policies = tmp_path / "policies"
    policies.mkdir()
    (policies / "dr.md").write_text("Disaster recovery drills run every quarter.", encoding="utf-8")
    src, dest = tmp_path / "q.csv", tmp_path / "out.csv"
    write_questionnaire(src, ["Do you run disaster recovery drills?"])

    assert main([str(src), str(dest), "--policies", str(policies), "--model-id", "m-1", "--region", "eu-west-1"]) == 0
    assert created == {"model_id": "m-1", "region": "eu-west-1"}
    assert "1 ready" in capsys.readouterr().out


def test_cli_refuses_a_policy_folder_with_no_policy_text(tmp_path, capsys):
    (tmp_path / "empty").mkdir()
    src = tmp_path / "q.csv"
    write_questionnaire(src, ["Anything?"])
    code = main([str(src), str(tmp_path / "out.csv"), "--policies", str(tmp_path / "empty")])
    assert code == 1
    assert "No .txt or .md policy text" in capsys.readouterr().err
    assert not (tmp_path / "out.csv").exists()  # nothing half-written

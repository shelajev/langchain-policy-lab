import json

from langchain_core.language_models.fake_chat_models import FakeListChatModel
import pytest
from pydantic import ValidationError

from langchain_enterprise.chain import PolicyAssistant
from langchain_enterprise.cli import main
from langchain_enterprise.evaluation import CASES, evaluate
from langchain_enterprise.ingestion import load_policies
from langchain_enterprise.models import get_model


def test_ingestion(policies):
    documents = load_policies(policies)
    assert len(documents) == 13
    assert len({document.metadata["source"] for document in documents}) == 4
    assert len({document.metadata["chunk_id"] for document in documents}) == len(documents)
    assert all(document.page_content and document.metadata["section"] and document.metadata["title"] for document in documents)


@pytest.mark.parametrize("question,status,fact,source", CASES)
def test_evaluation_cases(assistant, question, status, fact, source):
    answer = assistant.ask(question)
    assert answer["status"] == status
    assert fact in answer["answer"]
    if source:
        assert any(citation["source"] == source for citation in answer["citations"])
        assert all(citation in [document.metadata for document in assistant.documents]
                   for citation in answer["citations"])
    else:
        assert answer["citations"] == []


def test_suite(assistant):
    assert evaluate(assistant)["passed"]


def test_retriever_ranking_and_bounds(assistant):
    result = assistant.retriever.invoke("receipt threshold")
    assert result[0].metadata["chunk_id"] == "expense_policy:1"
    assert len(result) <= 2
    assert assistant.retriever.invoke("what is the policy") == []


def test_fake_answers_changed_corpus_not_canned(policies, tmp_path):
    for source in policies.glob("*.md"):
        (tmp_path / source.name).write_text(source.read_text().replace("$90", "$95"))
    changed = PolicyAssistant(tmp_path)
    assert "$95" in changed.ask("Tier 1 meal allowance")["answer"]
    assert changed.tools["meal"].invoke({"city_tier": 1, "days": 3})["total_usd"] == 285


@pytest.mark.parametrize("tier,daily", [(1, 90), (2, 70), (3, 50)])
def test_meal_tool(assistant, tier, daily):
    result = assistant.tools["meal"].invoke({"city_tier": tier, "days": 3})
    assert result["total_usd"] == daily * 3
    assert result["citation"]["chunk_id"] == "travel_policy:1"


@pytest.mark.parametrize("inputs", [
    {"city_tier": 0, "days": 1}, {"city_tier": 4, "days": 1},
    {"city_tier": 1, "days": 0}, {"city_tier": 1, "days": 31},
    {"city_tier": True, "days": 1}, {"city_tier": "1", "days": 1},
    {"city_tier": 1, "days": 1, "path": "/etc/passwd"},
])
def test_invalid_meal_inputs(assistant, inputs):
    with pytest.raises(ValidationError):
        assistant.tools["meal"].invoke(inputs)


@pytest.mark.parametrize("amount,required", [(0, False), (24.99, False), (25, True), (25.01, True), (100_000, True)])
def test_receipt_boundary(assistant, amount, required):
    assert assistant.tools["receipt"].invoke({"amount": amount})["receipt_required"] == required


@pytest.mark.parametrize("amount", [-1, 100_001, float("nan"), float("inf"), True, "25"])
def test_invalid_receipt_inputs(assistant, amount):
    with pytest.raises(ValidationError):
        assistant.tools["receipt"].invoke({"amount": amount})


@pytest.mark.parametrize("response,error", [
    ("not json", "model_or_output_failure"),
    ('{"answer":"invented", "chunk_ids": ["not-a-source"]}', "invalid_citations"),
    ('{"answer":"empty", "chunk_ids": []}', "model_or_output_failure"),
    ('{"answer":"duplicates", "chunk_ids": ["expense_policy:1", "expense_policy:1"]}', "invalid_citations"),
])
def test_invalid_model_output_fails_closed(policies, response, error):
    assistant = PolicyAssistant(policies, model=FakeListChatModel(responses=[response]))
    result = assistant.ask("receipt threshold")
    assert result["status"] == "failure"
    assert result["error"] == error
    assert not result["citations"]


def test_model_exception_is_sanitized(assistant, monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("private-token-must-not-leak")
    monkeypatch.setattr(assistant, "chain", type("Broken", (), {"invoke": broken})())
    result = assistant.ask("receipt threshold")
    assert result["status"] == "failure"
    assert "private-token" not in json.dumps(result)


def test_unsupported_never_calls_model(assistant, monkeypatch):
    def unexpected(*args, **kwargs):
        raise AssertionError("Unsupported questions must not invoke the model")
    monkeypatch.setattr(assistant, "chain", type("Unexpected", (), {"invoke": unexpected})())
    assert assistant.ask("holiday bonus")["status"] == "unsupported"


def test_provider_explicit_approval(monkeypatch):
    with pytest.raises(ValueError, match="approve-live"):
        get_model("gemini")
    with pytest.raises(ValueError, match="credential"):
        get_model("gemini", approve_live=True)
    with pytest.raises(ValueError, match="Unknown"):
        get_model("anything")
    import sys
    from types import SimpleNamespace
    captured = {}
    fake = FakeListChatModel(responses=["not used"])
    def constructor(**kwargs):
        captured.update(kwargs)
        return fake
    monkeypatch.setenv("GEMINI_API_KEY", "synthetic-test-placeholder")
    monkeypatch.setitem(sys.modules, "langchain_google_genai", SimpleNamespace(ChatGoogleGenerativeAI=constructor))
    assert get_model("gemini", approve_live=True) is fake
    assert captured == {"model": "gemini-2.5-flash", "temperature": 0,
                        "max_retries": 0, "timeout": 30, "max_output_tokens": 512}


def test_invalid_corpus(tmp_path):
    with pytest.raises(ValueError, match="No Markdown"):
        load_policies(tmp_path)
    (tmp_path / "bad.md").write_text("## Section\nNo title")
    with pytest.raises(ValueError, match="title"):
        load_policies(tmp_path)


def test_missing_tool_section(assistant):
    from langchain_enterprise.tools import policy_tools
    with pytest.raises(ValueError, match="missing"):
        policy_tools([])["meal"].invoke({"city_tier": 1, "days": 1})


@pytest.mark.parametrize("question", ["", " " * 10, "x" * 2001])
def test_invalid_question(assistant, question):
    assert assistant.ask(question)["error"] == "invalid_question"


def test_cli(policies, capsys):
    assert main(["--policies", str(policies), "--query", "receipt threshold"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "grounded"
    assert main(["--policies", str(policies), "--eval-suite"]) == 0
    assert json.loads(capsys.readouterr().out)["passed"]
    assert main(["--policies", str(policies), "--tool", "meal", "--days", "3"]) == 0
    assert json.loads(capsys.readouterr().out)["total_usd"] == 270
    assert main(["--policies", str(policies), "--tool", "meal", "--days", "31"]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "failure"
    assert main(["--policies", "/nonexistent", "--eval-suite"]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "failure"

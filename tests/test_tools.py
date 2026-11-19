"""ツールのテスト（LLMもAPIキーも使わない）。"""

import json

from app import tools


def test_glossary_ids_are_unique_and_related_links_exist():
    terms = tools.load_glossary()
    ids = [t["id"] for t in terms]
    assert len(ids) == len(set(ids))
    for t in terms:
        for r in t["related"]:
            assert r in ids, f"{t['id']} の related に存在しない id: {r}"


def test_search_finds_term_by_name_and_alias():
    for query in ["LoRA", "lora", "Low-Rank Adaptation"]:
        hits = json.loads(tools.search_glossary(query))
        assert hits[0]["term"] == "LoRA", query


def test_search_finds_course_specific_term():
    hits = json.loads(tools.search_glossary("lecNN-start"))
    assert hits[0]["term"] == "lecNN-start タグ"


def test_search_limits_number_of_results():
    hits = json.loads(tools.search_glossary("エージェント"))
    assert 1 <= len(hits) <= tools.MAX_RESULTS


def test_search_reports_not_found():
    assert "見つかりませんでした" in tools.search_glossary("存在しない用語xyz")


def test_lecture_summary():
    assert "エージェント" in tools.get_lecture_summary(3)
    assert "まだありません" in tools.get_lecture_summary(99)


def test_default_question_of_lecture1_is_answerable_from_glossary():
    """第1回の既定の質問（app.ask）は、第3回のエージェントが用語集で正しく答えられること。"""
    from app.ask import DEFAULT_QUESTION

    assert "3レベル" in DEFAULT_QUESTION
    hits = json.loads(tools.search_glossary("3レベル"))
    assert hits[0]["term"] == "宿題の3レベル"


def test_make_quiz_returns_four_choices_and_answer():
    quiz = tools.make_quiz("ファインチューニング")
    assert "問題:" in quiz
    assert "事前学習済みモデルを" in quiz
    assert quiz.count("\nA.") == 1 or "A. " in quiz
    assert "答え: C" in quiz
    assert "ファインチューニング" in quiz


def test_make_quiz_reports_not_found():
    assert "見つかりませんでした" in tools.make_quiz("存在しない用語xyz")


def test_save_learning_log_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "LEARNING_LOG_DIR", tmp_path)
    result = tools.save_learning_log("第3回テスト", "クイズの動作確認")
    files = list(tmp_path.glob("*.md"))
    assert len(files) == 1
    text = files[0].read_text(encoding="utf-8")
    assert "第3回テスト" in text
    assert "クイズの動作確認" in text
    assert files[0].name in result


def test_save_learning_log_appends_to_existing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(tools, "LEARNING_LOG_DIR", tmp_path)
    tools.save_learning_log("第3回テスト", "1回目")
    tools.save_learning_log("第3回テスト", "2回目")
    files = list(tmp_path.glob("*.md"))
    assert len(files) == 1
    text = files[0].read_text(encoding="utf-8")
    assert "1回目" in text and "2回目" in text


def test_make_quiz_is_called_with_test_model():
    from pydantic_ai.messages import ToolReturnPart
    from pydantic_ai.models.test import TestModel
    from app.agent import agent
    model = TestModel(call_tools=["make_quiz"])
    with agent.override(model=model):
        result = agent.run_sync("ファインチューニングのクイズを作って")
    returns = [p for m in result.all_messages() for p in m.parts if isinstance(p, ToolReturnPart)]
    assert returns and returns[0].tool_name == "make_quiz"
    assert "答え:" in str(returns[0].content)


def test_save_learning_log_requires_approval_with_test_model(tmp_path, monkeypatch):
    import pytest
    from pydantic_ai.models.test import TestModel
    from app.agent import agent
    monkeypatch.setattr(tools, "LEARNING_LOG_DIR", tmp_path)
    model = TestModel(call_tools=["save_learning_log"])
    with pytest.raises(Exception, match="DeferredToolRequests"):
        with agent.override(model=model):
            agent.run_sync("学習ログを保存して")
    assert list(tmp_path.glob("*.md")) == []

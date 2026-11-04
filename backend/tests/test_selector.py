import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from database.sqlite_client import get_db
from questions.loader import load_questions_from_file
from questions.chroma_client import embed_questions
from questions.selector import select_question, select_exam_set

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "sample_questions.json")


@pytest.fixture
def setup_chroma(tmp_path):
    questions = load_questions_from_file(FIXTURE_PATH)
    chroma_path = str(tmp_path / "chroma")
    embed_questions(questions, collection_name="test_selector", chroma_path=chroma_path)
    return chroma_path


def test_select_question_returns_question(setup_chroma, tmp_path):
    db = get_db(":memory:")
    question = select_question(
        db=db,
        provider="AWS",
        exclude_ids=[],
        chroma_path=setup_chroma,
        collection_name="test_selector",
    )
    assert question is not None
    assert question.id
    assert question.provider == "AWS"


def test_select_no_repeat_in_session(setup_chroma, tmp_path):
    db = get_db(":memory:")
    q1 = select_question(db=db, provider="AWS", exclude_ids=[], chroma_path=setup_chroma, collection_name="test_selector")
    q2 = select_question(db=db, provider="AWS", exclude_ids=[q1.id], chroma_path=setup_chroma, collection_name="test_selector")
    assert q1.id != q2.id


def test_select_fallback_on_empty_history(setup_chroma):
    db = get_db(":memory:")
    question = select_question(
        db=db,
        provider="AWS",
        exclude_ids=[],
        chroma_path=setup_chroma,
        collection_name="test_selector",
    )
    assert question is not None


def test_select_exam_set_returns_n_questions(setup_chroma):
    db = get_db(":memory:")
    questions = select_exam_set(
        db=db,
        provider="AWS",
        n=3,
        chroma_path=setup_chroma,
        collection_name="test_selector",
    )
    assert len(questions) == 3
    ids = [q.id for q in questions]
    assert len(set(ids)) == 3

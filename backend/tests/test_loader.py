import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from questions.loader import load_questions_from_file
from questions.chroma_client import embed_questions, query_questions


FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "sample_questions.json")


def test_load_questions_from_file():
    questions = load_questions_from_file(FIXTURE_PATH)
    assert len(questions) > 0
    assert questions[0].id
    assert questions[0].text
    assert len(questions[0].options) == 4


def test_load_and_query_questions(tmp_path):
    questions = load_questions_from_file(FIXTURE_PATH)
    collection_name = "test_load_query"
    chroma_path = str(tmp_path / "chroma")

    embed_questions(questions, collection_name=collection_name, chroma_path=chroma_path)
    results = query_questions(
        collection_name=collection_name,
        chroma_path=chroma_path,
        domain="TECHNOLOGY",
        exclude_ids=[],
        n=2,
    )
    assert len(results) == 2
    assert all(q.domain == "TECHNOLOGY" for q in results)


def test_query_excludes_ids(tmp_path):
    questions = load_questions_from_file(FIXTURE_PATH)
    chroma_path = str(tmp_path / "chroma")
    embed_questions(questions, collection_name="test_exclude", chroma_path=chroma_path)

    all_tech = query_questions(
        collection_name="test_exclude",
        chroma_path=chroma_path,
        domain="TECHNOLOGY",
        exclude_ids=[],
        n=10,
    )
    first_id = all_tech[0].id
    results = query_questions(
        collection_name="test_exclude",
        chroma_path=chroma_path,
        domain="TECHNOLOGY",
        exclude_ids=[first_id],
        n=10,
    )
    assert first_id not in [q.id for q in results]

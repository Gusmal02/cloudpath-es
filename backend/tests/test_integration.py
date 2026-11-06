"""Integration tests — hit real FastAPI endpoints with a real (temp) SQLite database."""
import os
import tempfile
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("data")
    db_path = str(db_dir / "test.db")
    chroma_path = str(db_dir / "chroma")
    questions_dir = str(tmp_path_factory.mktemp("questions"))

    os.environ["CLOUDPATH_DB_PATH"] = db_path
    os.environ["CLOUDPATH_CHROMA_PATH"] = chroma_path
    os.environ["CLOUDPATH_QUESTIONS_DIR"] = questions_dir

    # Import after env vars are set so get_settings() picks them up
    from config import get_settings
    get_settings.cache_clear()
    from questions.chroma_client import _get_client
    _get_client.cache_clear()

    from main import app
    with TestClient(app) as c:
        yield c

    get_settings.cache_clear()
    _get_client.cache_clear()
    os.environ.pop("CLOUDPATH_DB_PATH", None)
    os.environ.pop("CLOUDPATH_CHROMA_PATH", None)
    os.environ.pop("CLOUDPATH_QUESTIONS_DIR", None)


def test_health_check(client):
    """Backend health endpoint returns 200."""
    res = client.get("/health")
    assert res.status_code == 200


def test_domain_progress_empty(client):
    """domain_progress returns empty list for a provider with no answers yet."""
    res = client.get("/progress/domains", params={"provider": "AWS"})
    assert res.status_code == 200
    assert res.json() == []


def test_exam_start_no_questions_404(client):
    """Starting an exam with no questions loaded returns 404."""
    res = client.post("/exam/start", json={"provider": "AWS", "n_questions": 5})
    assert res.status_code == 404


def test_study_question_no_questions_404(client):
    """Fetching a study question with empty corpus returns 404."""
    res = client.get("/study/question", params={"provider": "AWS"})
    assert res.status_code == 404


def test_study_answer_unknown_question_id_404(client):
    """POST /study/answer with an unknown question_id returns 404 before chosen validation."""
    res = client.post("/study/answer", json={"question_id": "nonexistent"})
    assert res.status_code == 404


def test_exam_answer_empty_chosen_422(client):
    """POST /exam/answer with chosen_indices=[] returns 422."""
    res = client.post(
        "/exam/answer",
        json={
            "session_id": "00000000-0000-0000-0000-000000000000",
            "question_id": "q1",
            "chosen_indices": [],
        },
    )
    assert res.status_code == 422

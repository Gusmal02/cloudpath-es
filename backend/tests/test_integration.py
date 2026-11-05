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

    os.environ["DB_PATH"] = db_path
    os.environ["CHROMA_PATH"] = chroma_path

    # Import after env vars are set so get_settings() picks them up
    from config import get_settings
    get_settings.cache_clear()

    from main import app
    with TestClient(app) as c:
        yield c

    get_settings.cache_clear()


def test_health_check(client):
    """Backend responds on root path."""
    res = client.get("/")
    assert res.status_code in (200, 404)  # 404 is fine — no root route required


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


def test_study_answer_missing_chosen_422(client):
    """POST /study/answer without chosen_index or chosen_indices returns 422."""
    res = client.post("/study/answer", json={"question_id": "nonexistent"})
    assert res.status_code == 422


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

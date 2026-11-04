import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from questions.models import Question, Domain, Provider, Difficulty


SAMPLE_QUESTION = Question(
    id="test-001",
    text="¿Qué servicio usarías para almacenar objetos?",
    options=["EBS", "S3", "EFS", "RDS"],
    correct_index=1,
    explanation="S3 es el almacenamiento de objetos de AWS.",
    domain=Domain.TECHNOLOGY,
    provider=Provider.AWS,
    difficulty=Difficulty.EASY,
)

SAMPLE_QUESTIONS = [
    Question(
        id=f"test-{i:03d}",
        text=f"Pregunta de prueba {i}",
        options=["A", "B", "C", "D"],
        correct_index=0,
        explanation=f"Explicación {i}",
        domain=Domain.TECHNOLOGY,
        provider=Provider.AWS,
        difficulty=Difficulty.EASY,
    )
    for i in range(5)
]


@pytest.fixture
def client(tmp_path):
    os.environ["CLOUDPATH_DB_PATH"] = str(tmp_path / "test.db")
    os.environ["CLOUDPATH_CHROMA_PATH"] = str(tmp_path / "chroma")
    os.environ["CLOUDPATH_PORT_FILE"] = str(tmp_path / ".port")

    from main import app
    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_exam_start_returns_session_and_questions(client):
    with patch("routers.exam.select_exam_set", return_value=SAMPLE_QUESTIONS):
        response = client.post("/exam/start", json={"provider": "AWS", "n_questions": 5})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert len(data["questions"]) == 5


def test_exam_options_are_shuffled_differently(client):
    with patch("routers.exam.select_exam_set", return_value=[SAMPLE_QUESTION]):
        r1 = client.post("/exam/start", json={"provider": "AWS", "n_questions": 1})
        r2 = client.post("/exam/start", json={"provider": "AWS", "n_questions": 1})
    options1 = r1.json()["questions"][0]["options"]
    options2 = r2.json()["questions"][0]["options"]
    assert set(options1) == set(options2)


def test_exam_answer_correct(client):
    with patch("routers.exam.select_exam_set", return_value=[SAMPLE_QUESTION]):
        start = client.post("/exam/start", json={"provider": "AWS", "n_questions": 1}).json()

    session_id = start["session_id"]
    shuffled_options = start["questions"][0]["options"]
    correct_text = SAMPLE_QUESTION.options[SAMPLE_QUESTION.correct_index]
    chosen_index = shuffled_options.index(correct_text)

    response = client.post("/exam/answer", json={
        "session_id": session_id,
        "question_id": SAMPLE_QUESTION.id,
        "chosen_index": chosen_index,
    })
    assert response.status_code == 200
    assert response.json()["is_correct"] is True


def test_exam_result(client):
    with patch("routers.exam.select_exam_set", return_value=[SAMPLE_QUESTION]):
        start = client.post("/exam/start", json={"provider": "AWS", "n_questions": 1}).json()

    client.post("/exam/answer", json={
        "session_id": start["session_id"],
        "question_id": SAMPLE_QUESTION.id,
        "chosen_index": 0,
    })

    response = client.get(f"/exam/result/{start['session_id']}")
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "total" in data
    assert "by_domain" in data


def test_study_question(client):
    with patch("routers.study.select_question", return_value=SAMPLE_QUESTION):
        response = client.get("/study/question", params={"provider": "AWS", "exclude_ids": []})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == SAMPLE_QUESTION.id


def test_study_answer_returns_explanation(client):
    with patch("routers.study.select_question", return_value=SAMPLE_QUESTION):
        q = client.get("/study/question", params={"provider": "AWS", "exclude_ids": []}).json()

    response = client.post("/study/answer", json={
        "question_id": SAMPLE_QUESTION.id,
        "chosen_index": SAMPLE_QUESTION.correct_index,
    })
    assert response.status_code == 200
    data = response.json()
    assert "is_correct" in data
    assert "explanation" in data


def test_progress_domains(client):
    response = client.get("/progress/domains", params={"provider": "AWS"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

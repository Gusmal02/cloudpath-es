import json
import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    questions_dir = tmp_path / "questions"
    questions_dir.mkdir()
    sample = [
        {
            "id": "q1",
            "text": "¿Qué es AWS S3?",
            "options": ["A", "B", "C", "D"],
            "correct_index": 0,
            "explanation": "S3 es almacenamiento de objetos.",
            "domain": "TECHNOLOGY",
            "provider": "AWS",
            "difficulty": "easy",
        }
    ]
    (questions_dir / "test.json").write_text(json.dumps(sample), encoding="utf-8")

    monkeypatch.setenv("CLOUDPATH_QUESTIONS_DIR", str(questions_dir))
    monkeypatch.setenv("CLOUDPATH_CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("CLOUDPATH_DB_PATH", ":memory:")

    from main import app
    return TestClient(app)


def test_load_questions_success(client):
    resp = client.post("/admin/load-questions")
    assert resp.status_code == 200
    data = resp.json()
    assert data["loaded"] == 1
    assert "test.json" in data["files"]
    assert data["errors"] == []


def test_load_questions_missing_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("CLOUDPATH_QUESTIONS_DIR", str(tmp_path / "nonexistent"))
    monkeypatch.setenv("CLOUDPATH_CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("CLOUDPATH_DB_PATH", ":memory:")
    from main import app
    c = TestClient(app)
    resp = c.post("/admin/load-questions")
    assert resp.status_code == 404

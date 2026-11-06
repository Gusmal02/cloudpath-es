"""Integration tests — hit real FastAPI endpoints with a real (temp) SQLite database."""
import os
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


def test_study_answer_missing_chosen_422(client):
    """POST /study/answer with no chosen field returns 422 (chosen validated before Chroma lookup)."""
    res = client.post("/study/answer", json={"question_id": "nonexistent"})
    assert res.status_code == 422


def test_study_answer_unknown_question_id_404(client):
    """POST /study/answer with unknown question_id but valid chosen returns 404."""
    res = client.post("/study/answer", json={"question_id": "nonexistent", "chosen_indices": [0]})
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


# ---------------------------------------------------------------------------
# Fixture: seed Chroma + DB with known questions so the happy-path tests work
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def seeded_client(tmp_path_factory):
    """Client backed by a Chroma collection pre-loaded with 5 AWS questions."""
    import json as _json
    db_dir = tmp_path_factory.mktemp("seeded_data")
    db_path = str(db_dir / "test.db")
    chroma_path = str(db_dir / "chroma")
    questions_dir = str(db_dir / "questions")
    os.makedirs(questions_dir, exist_ok=True)

    # Write a minimal questions JSON file so the embed_on_startup path runs
    questions = [
        {
            "id": f"aws-q{i}",
            "text": f"AWS question {i} about cloud concepts?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_index": 0,
            "correct_indices": [0],
            "explanation": f"Explanation for question {i}",
            "domain": "CLOUD_CONCEPTS",
            "provider": "AWS",
            "difficulty": "easy",
            "num_correct": 1,
        }
        for i in range(5)
    ]
    q_file = os.path.join(questions_dir, "aws.json")
    with open(q_file, "w", encoding="utf-8") as f:
        _json.dump(questions, f)

    os.environ["CLOUDPATH_DB_PATH"] = db_path
    os.environ["CLOUDPATH_CHROMA_PATH"] = chroma_path
    os.environ["CLOUDPATH_QUESTIONS_DIR"] = questions_dir

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


# ---------------------------------------------------------------------------
# Happy-path end-to-end: start exam → answer all → result
# ---------------------------------------------------------------------------

def test_e2e_exam_full_flow(seeded_client):
    """
    E2E: start a 3-question exam, answer all, fetch result.
    Verifies score, by_domain entries, and that domain_progress is updated.
    """
    client = seeded_client
    n = 3

    # 1. Start exam
    start_res = client.post("/exam/start", json={"provider": "AWS", "n_questions": n})
    assert start_res.status_code == 200, start_res.text
    start_data = start_res.json()
    session_id = start_data["session_id"]
    questions = start_data["questions"]
    assert len(questions) == n

    # Anti-cheat: public questions must NOT expose answers
    for q in questions:
        assert "correct_index" not in q
        assert "correct_indices" not in q
        assert "explanation" not in q

    # 2. Answer all questions: pick index 0 (which is correct after shuffle)
    # The seed always places correct_index=0; after shuffle reverse_map
    # maps old-0 to new position. We submit index 0 and accept whatever result.
    correct_count = 0
    for q in questions:
        ans_res = client.post(
            "/exam/answer",
            json={
                "session_id": session_id,
                "question_id": q["id"],
                "chosen_indices": [0],
            },
        )
        assert ans_res.status_code == 200, ans_res.text
        fb = ans_res.json()
        # Answer response MUST include explanation and correct_indices
        assert "explanation" in fb
        assert "correct_indices" in fb
        assert isinstance(fb["is_correct"], bool)
        if fb["is_correct"]:
            correct_count += 1

    # 3. Get result
    result_res = client.get(f"/exam/result/{session_id}")
    assert result_res.status_code == 200, result_res.text
    result = result_res.json()
    assert result["session_id"] == session_id
    assert result["total"] == n
    assert result["score"] == correct_count

    # by_domain must include CLOUD_CONCEPTS (all 5 seed questions are that domain)
    domains = {d["domain"]: d for d in result["by_domain"]}
    assert "CLOUD_CONCEPTS" in domains
    cc = domains["CLOUD_CONCEPTS"]
    assert cc["total"] == n
    assert cc["correct"] == correct_count
    assert 0.0 <= cc["pct"] <= 100.0

    # 4. domain_progress must be updated
    prog_res = client.get("/progress/domains", params={"provider": "AWS"})
    assert prog_res.status_code == 200
    prog = {d["domain"]: d for d in prog_res.json()}
    assert "CLOUD_CONCEPTS" in prog
    assert prog["CLOUD_CONCEPTS"]["total"] >= n


def test_e2e_exam_duplicate_answer_idempotent(seeded_client):
    """
    Submitting the same answer twice must return the same is_correct value both times.
    """
    client = seeded_client
    start_res = client.post("/exam/start", json={"provider": "AWS", "n_questions": 1})
    assert start_res.status_code == 200, start_res.text
    session_id = start_res.json()["session_id"]
    q_id = start_res.json()["questions"][0]["id"]

    payload = {"session_id": session_id, "question_id": q_id, "chosen_indices": [0]}
    r1 = client.post("/exam/answer", json=payload)
    r2 = client.post("/exam/answer", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["is_correct"] == r2.json()["is_correct"]


def test_e2e_study_flow(seeded_client):
    """
    E2E: fetch a study question, answer it, verify feedback fields.
    """
    client = seeded_client

    # Fetch question
    q_res = client.get("/study/question", params={"provider": "AWS"})
    assert q_res.status_code == 200, q_res.text
    q = q_res.json()
    assert "id" in q
    # Anti-cheat
    assert "correct_index" not in q
    assert "correct_indices" not in q
    assert "explanation" not in q

    # Answer it
    ans_res = client.post(
        "/study/answer",
        json={"question_id": q["id"], "chosen_indices": [0]},
    )
    assert ans_res.status_code == 200, ans_res.text
    fb = ans_res.json()
    assert "explanation" in fb
    assert "correct_indices" in fb
    assert isinstance(fb["is_correct"], bool)

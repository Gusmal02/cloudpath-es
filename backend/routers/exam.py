import logging
from fastapi import APIRouter, Depends, HTTPException
import json
import sqlite3

logger = logging.getLogger(__name__)
from config import get_settings
from database.sqlite_client import get_db
from exam.models import StartExamRequest, AnswerRequest, ExamResult
from exam.session import start_exam, submit_answer, get_result
from questions.selector import select_exam_set
from questions.chroma_client import get_question_by_id, query_questions

router = APIRouter(prefix="/exam", tags=["exam"])


def _get_db():
    settings = get_settings()
    db = get_db(settings.db_path)
    try:
        yield db
    finally:
        db.close()


def _persist_session_questions(db: sqlite3.Connection, session_id: str, questions: list[dict]) -> None:
    db.executemany(
        "INSERT OR REPLACE INTO session_questions (session_id, question_id, correct_indices, domain, provider) VALUES (?, ?, ?, ?, ?)",
        [
            (session_id, sq["id"], json.dumps(sq["correct_indices"]), sq["domain"], sq["provider"])
            for sq in questions
        ],
    )
    db.commit()


def _load_question_data(db: sqlite3.Connection, session_id: str, question_id: str) -> dict | None:
    row = db.execute(
        "SELECT correct_indices, domain, provider FROM session_questions WHERE session_id = ? AND question_id = ?",
        (session_id, question_id),
    ).fetchone()
    if row is None:
        return None
    return {
        "correct_indices": json.loads(row["correct_indices"]),
        "domain": row["domain"],
        "provider": row["provider"],
    }


@router.post("/start")
def exam_start(req: StartExamRequest, db: sqlite3.Connection = Depends(_get_db)):
    settings = get_settings()
    questions = select_exam_set(
        db=db,
        provider=req.provider,
        n=req.n_questions,
        chroma_path=settings.chroma_path,
    )
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for this provider")

    result = start_exam(db=db, provider=req.provider, questions=questions)
    _persist_session_questions(db, result["session_id"], result["_internal"])

    return {"session_id": result["session_id"], "questions": result["questions"]}


@router.post("/answer")
def exam_answer(req: AnswerRequest, db: sqlite3.Connection = Depends(_get_db)):
    # Validate chosen before hitting the DB
    if req.chosen_indices is not None:
        chosen = req.chosen_indices
    elif req.chosen_index is not None:
        chosen = [req.chosen_index]
    else:
        chosen = None
    if not chosen:
        raise HTTPException(status_code=422, detail="chosen_index or chosen_indices required")

    question_data = _load_question_data(db, req.session_id, req.question_id)
    if question_data is None:
        raise HTTPException(status_code=404, detail="Question not found in session")

    is_correct = submit_answer(
        db=db,
        session_id=req.session_id,
        question_id=req.question_id,
        chosen_indices=chosen,
        correct_indices=question_data["correct_indices"],
        domain=question_data["domain"],
        provider=question_data["provider"],
    )
    # Fetch explanation and correct options from Chroma now that the answer is submitted
    settings = get_settings()
    q = get_question_by_id(req.question_id, "questions", settings.chroma_path)
    if q is None:
        logger.error("exam_answer: question %s not found in Chroma for session %s", req.question_id, req.session_id)
    return {
        "is_correct": is_correct,
        "correct_indices": question_data["correct_indices"],
        "correct_index": question_data["correct_indices"][0],
        "explanation": q.explanation if q else "[Explicación no disponible]",
    }


@router.get("/result/{session_id}", response_model=ExamResult)
def exam_result(session_id: str, db: sqlite3.Connection = Depends(_get_db)):
    row = db.execute("SELECT id FROM exam_sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return get_result(db=db, session_id=session_id)

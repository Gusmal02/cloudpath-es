from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from config import get_settings
from database.sqlite_client import get_db
from exam.models import StartExamRequest, AnswerRequest, ExamResult
from exam.session import start_exam, submit_answer, get_result
from questions.selector import select_exam_set
from questions.chroma_client import query_questions

router = APIRouter(prefix="/exam", tags=["exam"])

# In-memory store for question correct_index per session (shuffled answers need original)
_session_questions: dict[str, dict[str, dict]] = {}


def _get_db():
    settings = get_settings()
    db = get_db(settings.db_path)
    try:
        yield db
    finally:
        db.close()


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
    session_id = result["session_id"]

    # Store post-shuffle correct_indices (single or multi-answer)
    _session_questions[session_id] = {
        sq["id"]: {
            "correct_indices": sq["correct_indices"],
            "domain": sq["domain"],
            "provider": sq["provider"],
        }
        for sq in result["questions"]
    }

    return result


@router.post("/answer")
def exam_answer(req: AnswerRequest, db: sqlite3.Connection = Depends(_get_db)):
    session_data = _session_questions.get(req.session_id, {})
    question_data = session_data.get(req.question_id)

    if question_data is None:
        raise HTTPException(status_code=404, detail="Question not found in session")

    # Normalise: accept either chosen_index (legacy) or chosen_indices (multi)
    if req.chosen_indices is not None:
        chosen = req.chosen_indices
    elif req.chosen_index is not None:
        chosen = [req.chosen_index]
    else:
        raise HTTPException(status_code=422, detail="chosen_index or chosen_indices required")

    is_correct = submit_answer(
        db=db,
        session_id=req.session_id,
        question_id=req.question_id,
        chosen_indices=chosen,
        correct_indices=question_data["correct_indices"],
        domain=question_data["domain"],
        provider=question_data["provider"],
    )
    return {"is_correct": is_correct}


@router.get("/result/{session_id}", response_model=ExamResult)
def exam_result(session_id: str, db: sqlite3.Connection = Depends(_get_db)):
    return get_result(db=db, session_id=session_id)

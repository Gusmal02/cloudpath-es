import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from config import get_settings
from database.sqlite_client import get_db
from exam.models import StudyAnswerRequest
from exam.session import update_domain_progress
from questions.chroma_client import get_question_by_id
from questions.models import Difficulty, Domain, Provider
from questions.selector import select_question

router = APIRouter(prefix="/study", tags=["study"])


class PublicQuestion(BaseModel):
    id: str
    text: str
    options: list[str]
    num_correct: int
    domain: Domain
    provider: Provider
    difficulty: Difficulty


def _get_db():
    settings = get_settings()
    db = get_db(settings.db_path)
    try:
        yield db
    finally:
        db.close()


@router.get("/question")
def study_question(
    provider: Provider = Query(...),
    exclude_ids: list[str] = Query(default=[]),
    db: sqlite3.Connection = Depends(_get_db),
):
    settings = get_settings()
    question = select_question(
        db=db,
        provider=provider,
        exclude_ids=exclude_ids,
        chroma_path=settings.chroma_path,
    )
    if question is None:
        raise HTTPException(status_code=404, detail="No questions available")

    return PublicQuestion(
        id=question.id,
        text=question.text,
        options=question.options,
        num_correct=question.num_correct,
        domain=question.domain,
        provider=question.provider,
        difficulty=question.difficulty,
    )


@router.post("/answer")
def study_answer(req: StudyAnswerRequest, db: sqlite3.Connection = Depends(_get_db)):
    settings = get_settings()
    question = get_question_by_id(
        question_id=req.question_id,
        collection_name="questions",
        chroma_path=settings.chroma_path,
    )
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    chosen = req.chosen_indices if req.chosen_indices is not None else (
        [req.chosen_index] if req.chosen_index is not None else None
    )
    if not chosen:
        raise HTTPException(status_code=422, detail="chosen_index or chosen_indices required")

    is_correct = set(chosen) == set(question.all_correct_indices)
    update_domain_progress(db, question.domain, question.provider, is_correct)
    return {
        "is_correct": is_correct,
        "correct_indices": question.all_correct_indices,
        "correct_index": question.all_correct_indices[0],
        "explanation": question.explanation,
    }

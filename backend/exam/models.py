from pydantic import BaseModel, Field
from questions.models import Provider


class StartExamRequest(BaseModel):
    provider: Provider
    n_questions: int = Field(default=10, ge=1, le=65)


class AnswerRequest(BaseModel):
    session_id: str
    question_id: str
    chosen_index: int | None = None          # single-answer (legacy)
    chosen_indices: list[int] | None = None  # multi-answer


class StudyAnswerRequest(BaseModel):
    question_id: str
    chosen_index: int | None = None
    chosen_indices: list[int] | None = None


class DomainResult(BaseModel):
    domain: str
    correct: int
    total: int
    pct: float


class ExamResult(BaseModel):
    session_id: str
    score: int
    total: int
    by_domain: list[DomainResult]

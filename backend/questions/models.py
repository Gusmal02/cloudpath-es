from enum import StrEnum
from pydantic import BaseModel


class Domain(StrEnum):
    CLOUD_CONCEPTS = "CLOUD_CONCEPTS"
    SECURITY = "SECURITY"
    TECHNOLOGY = "TECHNOLOGY"
    BILLING = "BILLING"
    AI_ML = "AI_ML"


class Provider(StrEnum):
    AWS = "AWS"
    GCP = "GCP"
    AZURE = "AZURE"


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Question(BaseModel):
    id: str
    text: str
    options: list[str]
    correct_index: int
    correct_indices: list[int] | None = None  # set for multi-answer questions
    explanation: str
    domain: Domain
    provider: Provider
    difficulty: Difficulty = Difficulty.MEDIUM

    @property
    def all_correct_indices(self) -> list[int]:
        return self.correct_indices if self.correct_indices is not None else [self.correct_index]

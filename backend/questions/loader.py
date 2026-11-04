import json
from pathlib import Path
from questions.models import Question


def load_questions_from_file(path: str) -> list[Question]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Question(**item) for item in data]

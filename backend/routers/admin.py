from fastapi import APIRouter, HTTPException
from pathlib import Path
from config import get_settings
from questions.loader import load_questions_from_file
from questions.chroma_client import embed_questions

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/load-questions")
def load_questions(collection_name: str = "questions"):
    """Load all JSON question files from data/questions/ into ChromaDB."""
    settings = get_settings()
    questions_dir = Path(settings.questions_dir)

    if not questions_dir.exists():
        raise HTTPException(status_code=404, detail=f"Questions directory not found: {questions_dir}")

    files = list(questions_dir.glob("*.json"))
    if not files:
        raise HTTPException(status_code=404, detail="No JSON files found in questions directory")

    all_questions = []
    errors = []
    for f in files:
        try:
            all_questions.extend(load_questions_from_file(str(f)))
        except Exception as e:
            errors.append({"file": f.name, "error": str(e)})

    if not all_questions:
        raise HTTPException(status_code=422, detail={"message": "No questions loaded", "errors": errors})

    embed_questions(all_questions, collection_name=collection_name, chroma_path=settings.chroma_path)

    return {
        "loaded": len(all_questions),
        "files": [f.name for f in files],
        "errors": errors,
    }

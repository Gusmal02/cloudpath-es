from fastapi import APIRouter, Depends, Query
import sqlite3
from config import get_settings
from database.sqlite_client import get_db

router = APIRouter(prefix="/progress", tags=["progress"])


def _get_db():
    settings = get_settings()
    db = get_db(settings.db_path)
    try:
        yield db
    finally:
        db.close()


@router.get("/domains")
def get_domain_progress(provider: str = Query(...), db: sqlite3.Connection = Depends(_get_db)):
    rows = db.execute(
        "SELECT domain, correct_count, total_count FROM domain_progress WHERE provider = ?",
        (provider,),
    ).fetchall()
    return [
        {
            "domain": row["domain"],
            "correct": row["correct_count"],
            "total": row["total_count"],
            "pct": round(row["correct_count"] / row["total_count"] * 100, 1) if row["total_count"] else 0.0,
        }
        for row in rows
    ]

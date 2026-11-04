import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.sqlite_client import get_db


def test_schema_creates_tables():
    db = get_db(":memory:")
    cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert {"exam_sessions", "user_answers", "domain_progress"} <= tables


def test_get_db_returns_connection():
    db = get_db(":memory:")
    assert db is not None
    result = db.execute("SELECT 1").fetchone()
    assert result[0] == 1

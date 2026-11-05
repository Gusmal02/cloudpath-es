import random
import sqlite3
import uuid
from datetime import datetime, timezone
from questions.models import Question
from exam.models import ExamResult, DomainResult


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def update_domain_progress(
    db: sqlite3.Connection,
    domain: str,
    provider: str,
    is_correct: bool,
) -> None:
    db.execute(
        """
        INSERT INTO domain_progress (domain, provider, correct_count, total_count, last_updated)
        VALUES (?, ?, ?, 1, ?)
        ON CONFLICT(domain, provider) DO UPDATE SET
            correct_count = correct_count + ?,
            total_count = total_count + 1,
            last_updated = ?
        """,
        (domain, provider, int(is_correct), _now(), int(is_correct), _now()),
    )
    db.commit()


def start_exam(db: sqlite3.Connection, provider: str, questions: list[Question]) -> dict:
    session_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO exam_sessions (id, started_at, mode, provider, total) VALUES (?, ?, ?, ?, ?)",
        (session_id, _now(), "exam", provider, len(questions)),
    )
    db.commit()

    shuffled_questions = []
    for q in questions:
        options = list(q.options)
        correct_texts = [options[i] for i in q.all_correct_indices]
        random.shuffle(options)
        new_correct_indices = [options.index(t) for t in correct_texts]
        shuffled_questions.append({
            "id": q.id,
            "text": q.text,
            "options": options,
            "correct_index": new_correct_indices[0],
            "correct_indices": new_correct_indices,
            "num_correct": len(new_correct_indices),
            "domain": q.domain,
            "provider": q.provider,
            "difficulty": q.difficulty,
            "explanation": q.explanation,
        })

    return {"session_id": session_id, "questions": shuffled_questions}


def update_domain_progress(
    db: sqlite3.Connection,
    domain: str,
    provider: str,
    is_correct: bool,
) -> None:
    """Actualiza la tabla domain_progress. Puede llamarse desde examen y desde estudio."""
    db.execute(
        """
        INSERT INTO domain_progress (domain, provider, correct_count, total_count, last_updated)
        VALUES (?, ?, ?, 1, ?)
        ON CONFLICT(domain, provider) DO UPDATE SET
            correct_count = correct_count + ?,
            total_count = total_count + 1,
            last_updated = ?
        """,
        (domain, provider, int(is_correct), _now(), int(is_correct), _now()),
    )
    db.commit()


def submit_answer(
    db: sqlite3.Connection,
    session_id: str,
    question_id: str,
    chosen_indices: list[int],
    correct_indices: list[int],
    domain: str,
    provider: str,
) -> bool:
    is_correct = set(chosen_indices) == set(correct_indices)
    chosen_index = chosen_indices[0]

    rows_changed = db.execute(
        "INSERT OR IGNORE INTO user_answers (id, session_id, question_id, chosen_index, is_correct, answered_at) VALUES (?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), session_id, question_id, chosen_index, int(is_correct), _now()),
    ).rowcount

    if rows_changed:  # skip domain_progress on duplicate submit
        update_domain_progress(db, domain, provider, is_correct)
    return is_correct


def get_result(db: sqlite3.Connection, session_id: str) -> ExamResult:
    answers = db.execute(
        "SELECT question_id, is_correct FROM user_answers WHERE session_id = ?",
        (session_id,),
    ).fetchall()

    score = sum(1 for a in answers if a["is_correct"])
    # Use total from the session record so unanswered questions count as wrong
    row = db.execute("SELECT total FROM exam_sessions WHERE id = ?", (session_id,)).fetchone()
    total = row["total"] if row else len(answers)

    domain_rows = db.execute(
        """
        SELECT sq.domain,
               COUNT(*) AS total_count,
               SUM(ua.is_correct) AS correct_count
        FROM user_answers ua
        JOIN session_questions sq
          ON ua.session_id = sq.session_id AND ua.question_id = sq.question_id
        WHERE ua.session_id = ?
        GROUP BY sq.domain
        """,
        (session_id,),
    ).fetchall()

    by_domain = [
        DomainResult(
            domain=row["domain"],
            correct=row["correct_count"],
            total=row["total_count"],
            pct=round(row["correct_count"] / row["total_count"] * 100, 1) if row["total_count"] else 0.0,
        )
        for row in domain_rows
    ]

    return ExamResult(session_id=session_id, score=score, total=total, by_domain=by_domain)

import json
import random
import sqlite3
import uuid
from datetime import datetime, timezone
from questions.models import Question
from exam.models import ExamResult, DomainResult


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# TRANSACTION RULE: Only the router/endpoint calls db.commit().
# Helper functions (start_exam, submit_answer, update_domain_progress, get_result)
# must NOT call db.commit() — except get_result, which owns the session-close commit.
# Rationale: a router groups multiple writes (e.g. INSERT session + INSERT questions)
# into one atomic commit so a failure mid-way does not leave zombie rows.


def start_exam(db: sqlite3.Connection, provider: str, questions: list[Question]) -> dict:
    session_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO exam_sessions (id, started_at, mode, provider, total) VALUES (?, ?, ?, ?, ?)",
        (session_id, _now(), "exam", provider, len(questions)),
    )

    public_questions = []
    internal_questions = []
    for q in questions:
        indices = list(range(len(q.options)))
        random.shuffle(indices)
        options = [q.options[i] for i in indices]
        reverse_map = {old: new for new, old in enumerate(indices)}
        new_correct_indices = [reverse_map[i] for i in q.all_correct_indices]
        public_questions.append({
            "id": q.id,
            "text": q.text,
            "options": options,
            "num_correct": len(new_correct_indices),
            "domain": q.domain,
            "provider": q.provider,
            "difficulty": q.difficulty,
            # correct_* and explanation omitted — returned by /exam/answer to prevent cheating
        })
        internal_questions.append({
            "id": q.id,
            "correct_indices": new_correct_indices,
            "domain": q.domain,
            "provider": q.provider,
        })

    return {
        "session_id": session_id,
        "questions": public_questions,
        "_internal": internal_questions,
    }


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


def submit_answer(
    db: sqlite3.Connection,
    session_id: str,
    question_id: str,
    chosen_indices: list[int],
    correct_indices: list[int],
    domain: str,
    provider: str,
) -> bool:
    # Return stored result on duplicate submit (avoids feedback/score mismatch)
    existing = db.execute(
        "SELECT is_correct FROM user_answers WHERE session_id = ? AND question_id = ?",
        (session_id, question_id),
    ).fetchone()
    if existing:
        return bool(existing["is_correct"])

    is_correct = set(chosen_indices) == set(correct_indices)
    chosen_index = chosen_indices[0] if len(chosen_indices) == 1 else None

    db.execute(
        "INSERT INTO user_answers (id, session_id, question_id, chosen_index, chosen_indices, is_correct, answered_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), session_id, question_id, chosen_index, json.dumps(chosen_indices), int(is_correct), _now()),
    )
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

    # Close the session (idempotent); rowcount > 0 means first close
    rows_changed = db.execute(
        "UPDATE exam_sessions SET finished_at = ?, score = ? WHERE id = ? AND finished_at IS NULL",
        (_now(), score, session_id),
    ).rowcount

    if rows_changed:
        # Register unanswered questions as incorrect in domain_progress (once only)
        unanswered = db.execute(
            """
            SELECT sq.domain, sq.provider
            FROM session_questions sq
            LEFT JOIN user_answers ua
              ON ua.session_id = sq.session_id AND ua.question_id = sq.question_id
            WHERE sq.session_id = ? AND ua.question_id IS NULL
            """,
            (session_id,),
        ).fetchall()
        for r in unanswered:
            update_domain_progress(db, r["domain"], r["provider"], is_correct=False)

    db.commit()

    domain_rows = db.execute(
        """
        SELECT sq.domain,
               COUNT(*)                        AS total_count,
               SUM(COALESCE(ua.is_correct, 0)) AS correct_count
        FROM session_questions sq
        LEFT JOIN user_answers ua
          ON ua.session_id = sq.session_id AND ua.question_id = sq.question_id
        WHERE sq.session_id = ?
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

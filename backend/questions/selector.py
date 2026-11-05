import random
import sqlite3
from questions.models import Question, Domain
from questions.chroma_client import query_questions


def _get_weak_domain(db: sqlite3.Connection, provider: str) -> str | None:
    cursor = db.execute(
        """
        SELECT domain, correct_count, total_count
        FROM domain_progress
        WHERE provider = ?
        ORDER BY CAST(correct_count AS REAL) / NULLIF(total_count, 0) ASC
        """,
        (provider,),
    )
    rows = cursor.fetchall()
    if not rows:
        return None
    return rows[0]["domain"]


def select_question(
    db: sqlite3.Connection,
    provider: str,
    exclude_ids: list[str],
    chroma_path: str = "data/chroma",
    collection_name: str = "questions",
) -> Question | None:
    domain = _get_weak_domain(db, provider)

    if domain is None:
        domain = random.choice([d.value for d in Domain])

    results = query_questions(
        collection_name=collection_name,
        chroma_path=chroma_path,
        domain=domain,
        exclude_ids=exclude_ids,
        n=1,
        provider=provider,
    )

    if results:
        return results[0]

    # fallback: try any domain for same provider
    for d in random.sample([d.value for d in Domain], len(Domain)):
        results = query_questions(
            collection_name=collection_name,
            chroma_path=chroma_path,
            domain=d,
            exclude_ids=exclude_ids,
            n=1,
            provider=provider,
        )
        if results:
            return results[0]

    return None


def select_exam_set(
    db: sqlite3.Connection,
    provider: str,
    n: int,
    chroma_path: str = "data/chroma",
    collection_name: str = "questions",
) -> list[Question]:
    domains = [d.value for d in Domain]
    per_domain = max(1, n // len(domains))
    extra = n - per_domain * len(domains)

    selected: list[Question] = []
    used_ids: list[str] = []

    for domain in domains:
        count = per_domain + (1 if extra > 0 else 0)
        extra = max(0, extra - 1)
        results = query_questions(
            collection_name=collection_name,
            chroma_path=chroma_path,
            domain=domain,
            exclude_ids=used_ids,
            n=count,
            provider=provider,
        )
        selected.extend(results)
        used_ids.extend([q.id for q in results])

    random.shuffle(selected)
    result = selected[:n]
    if len(result) < n:
        import logging
        logging.getLogger(__name__).warning(
            "select_exam_set: requested %d questions for provider=%s but only %d available",
            n, provider, len(result),
        )
    return result

import random
import sqlite3
from questions.models import Question, Domain
from questions.chroma_client import query_questions


def _get_weak_domain(db: sqlite3.Connection, provider: str) -> str:
    all_domains = {d.value for d in Domain}
    rows = db.execute(
        """
        SELECT domain, CAST(correct_count AS REAL) / NULLIF(total_count, 0) AS ratio
        FROM domain_progress
        WHERE provider = ?
        """,
        (provider,),
    ).fetchall()
    seen = {r["domain"] for r in rows}
    # Domains with no attempts get absolute priority
    untouched = list(all_domains - seen)
    if untouched:
        return random.choice(untouched)
    # Among seen domains, pick one of the worst performers via weighted sample
    rows_sorted = sorted(rows, key=lambda r: r["ratio"] or 0.0)
    # Weight: weakest gets highest chance; use rank-based weights
    weights = [len(rows_sorted) - i for i in range(len(rows_sorted))]
    return random.choices([r["domain"] for r in rows_sorted], weights=weights, k=1)[0]


def select_question(
    db: sqlite3.Connection,
    provider: str,
    exclude_ids: list[str],
    chroma_path: str = "data/chroma",
    collection_name: str = "questions",
) -> Question | None:
    domain = _get_weak_domain(db, provider)
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
    import logging
    logger = logging.getLogger(__name__)

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

    # Second pass: fill deficit by pulling extras from domains with more stock
    deficit = n - len(selected)
    if deficit > 0:
        for domain in random.sample(domains, len(domains)):
            if deficit <= 0:
                break
            extras = query_questions(
                collection_name=collection_name,
                chroma_path=chroma_path,
                domain=domain,
                exclude_ids=used_ids,
                n=deficit,
                provider=provider,
            )
            selected.extend(extras)
            used_ids.extend([q.id for q in extras])
            deficit -= len(extras)

    random.shuffle(selected)
    result = selected[:n]
    if len(result) < n:
        logger.warning(
            "select_exam_set: requested %d questions for provider=%s but only %d available",
            n, provider, len(result),
        )
    return result

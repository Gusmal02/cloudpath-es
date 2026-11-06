import json
import random
from functools import lru_cache

import chromadb
from chromadb.utils import embedding_functions
from questions.models import Question


def _parse_options(raw: str) -> list[str]:
    if not raw:
        return []
    try:
        result = json.loads(raw)
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        return [o for o in raw.split("|") if o]


@lru_cache(maxsize=4)
def _get_client(chroma_path: str) -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=chroma_path)


def _get_collection(collection_name: str, chroma_path: str):
    client = _get_client(chroma_path)
    ef = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def embed_questions(
    questions: list[Question],
    collection_name: str,
    chroma_path: str = "data/chroma",
) -> None:
    if not questions:
        return

    collection = _get_collection(collection_name, chroma_path)
    collection.upsert(
        ids=[q.id for q in questions],
        documents=[q.text for q in questions],
        metadatas=[
            {
                "domain": q.domain,
                "provider": q.provider,
                "difficulty": q.difficulty,
                "options": json.dumps(q.options),
                "correct_index": q.correct_index,
                "correct_indices": json.dumps(q.all_correct_indices),
                "explanation": q.explanation,
            }
            for q in questions
        ],
    )


def get_question_by_id(
    question_id: str,
    collection_name: str,
    chroma_path: str,
) -> Question | None:
    collection = _get_collection(collection_name, chroma_path)
    result = collection.get(ids=[question_id])
    if not result["ids"]:
        return None
    meta = result["metadatas"][0]
    text = result["documents"][0]
    raw_indices = meta.get("correct_indices")
    correct_indices = json.loads(raw_indices) if raw_indices else None
    options = _parse_options(meta.get("options", ""))
    return Question(
        id=question_id,
        text=text,
        options=options,
        correct_index=int(meta["correct_index"]),
        correct_indices=correct_indices,
        explanation=meta["explanation"],
        domain=meta["domain"],
        provider=meta["provider"],
        difficulty=meta["difficulty"],
    )


def query_questions(
    collection_name: str,
    chroma_path: str,
    domain: str,
    exclude_ids: list[str],
    n: int,
    provider: str | None = None,
) -> list[Question]:
    collection = _get_collection(collection_name, chroma_path)

    if provider:
        where = {"$and": [{"domain": {"$eq": domain}}, {"provider": {"$eq": provider}}]}
    else:
        where = {"domain": {"$eq": domain}}
    results = collection.get(where=where, limit=n + len(exclude_ids) + 10)

    questions = []
    for i, qid in enumerate(results["ids"]):
        if qid in exclude_ids:
            continue
        meta = results["metadatas"][i]
        text = results["documents"][i]
        raw_indices = meta.get("correct_indices")
        correct_indices = json.loads(raw_indices) if raw_indices else None
        opts = _parse_options(meta.get("options", ""))
        questions.append(
            Question(
                id=qid,
                text=text,
                options=opts,
                correct_index=int(meta["correct_index"]),
                correct_indices=correct_indices,
                explanation=meta["explanation"],
                domain=domain,
                provider=meta["provider"],
                difficulty=meta["difficulty"],
            )
        )

    return random.sample(questions, min(n, len(questions)))

import json
import random
from functools import lru_cache

import chromadb
from chromadb.utils import embedding_functions
from questions.models import Question


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
    collection = _get_collection(collection_name, chroma_path)
    existing = set(collection.get(ids=[q.id for q in questions])["ids"])

    new_questions = [q for q in questions if q.id not in existing]
    if not new_questions:
        return

    collection.upsert(
        ids=[q.id for q in new_questions],
        documents=[q.text for q in new_questions],
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
            for q in new_questions
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
    raw_options = meta.get("options", "[]")
    options = json.loads(raw_options) if raw_options.startswith("[") else raw_options.split("|")
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
    results = collection.get(where=where)

    questions = []
    for i, qid in enumerate(results["ids"]):
        if qid in exclude_ids:
            continue
        meta = results["metadatas"][i]
        text = results["documents"][i]
        raw_indices = meta.get("correct_indices")
        correct_indices = json.loads(raw_indices) if raw_indices else None
        raw_opts = meta.get("options", "[]")
        opts = json.loads(raw_opts) if raw_opts.startswith("[") else raw_opts.split("|")
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

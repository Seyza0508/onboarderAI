from __future__ import annotations

import pickle
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity

from app.rag.ingestion import RAG_INDEX_PATH, build_index


@dataclass
class RetrievedChunk:
    title: str
    source: str
    content: str
    score: float


@lru_cache(maxsize=1)
def _load_index(index_mtime: float) -> dict:
    del index_mtime
    with RAG_INDEX_PATH.open("rb") as f:
        return pickle.load(f)


def _get_index() -> dict:
    if not RAG_INDEX_PATH.exists():
        build_index(force_rebuild=True)
    mtime = Path(RAG_INDEX_PATH).stat().st_mtime
    return _load_index(mtime)


def retrieve_chunks(query: str, top_k: int = 4) -> list[RetrievedChunk]:
    query = query.strip()
    if not query:
        return []

    index = _get_index()
    vectorizer = index["vectorizer"]
    matrix = index["matrix"]
    docs = index["documents"]

    query_vector = vectorizer.transform([query])
    similarities = cosine_similarity(query_vector, matrix).flatten()
    if similarities.size == 0:
        return []

    top_indices = similarities.argsort()[::-1][:top_k]
    results: list[RetrievedChunk] = []
    for idx in top_indices:
        score = float(similarities[idx])
        if score <= 0:
            continue
        doc = docs[idx]
        results.append(
            RetrievedChunk(
                title=doc["title"],
                source=doc["source"],
                content=doc["content"],
                score=score,
            )
        )

    return results

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import RetrievalEvaluation
from app.rag.retriever import retrieve_chunks


def run_retrieval_eval(db: Session, query: str, expected_docs: list[str]) -> RetrievalEvaluation:
    chunks = retrieve_chunks(query, top_k=5)
    retrieved_docs = [chunk.source for chunk in chunks]
    overlap = len(set(expected_docs).intersection(set(retrieved_docs)))
    score = overlap / max(len(expected_docs), 1)
    row = RetrievalEvaluation(
        query=query,
        expected_docs=", ".join(expected_docs),
        retrieved_docs=", ".join(retrieved_docs),
        score=score,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

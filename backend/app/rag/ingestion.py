from __future__ import annotations

import pickle
from pathlib import Path

from app.rag.embedder import create_vectorizer

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOCS_DIR = PROJECT_ROOT / "data" / "unstructured"
RAG_INDEX_PATH = PROJECT_ROOT / "storage" / "rag_index.pkl"


def _split_text(text: str, max_chars: int = 850, overlap: int = 140) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)
            tail = current[-overlap:] if len(current) > overlap else current
            current = f"{tail}\n\n{paragraph}".strip()
        else:
            chunks.append(paragraph[:max_chars])
            current = paragraph[max_chars - overlap :]

    if current:
        chunks.append(current)

    return chunks


def build_index(force_rebuild: bool = False) -> Path:
    if RAG_INDEX_PATH.exists() and not force_rebuild:
        return RAG_INDEX_PATH

    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"Unstructured docs directory not found: {DOCS_DIR}")

    documents: list[dict] = []
    chunk_id = 1
    for path in sorted(DOCS_DIR.glob("*.md")):
        raw_text = path.read_text(encoding="utf-8")
        title = path.name.replace(".md", "").replace("_", " ").title()
        chunks = _split_text(raw_text)
        for chunk in chunks:
            documents.append(
                {
                    "chunk_id": chunk_id,
                    "title": title,
                    "source": path.name,
                    "source_path": str(path),
                    "content": chunk,
                }
            )
            chunk_id += 1

    if not documents:
        raise ValueError("No chunks were created from unstructured docs")

    vectorizer = create_vectorizer()
    matrix = vectorizer.fit_transform([doc["content"] for doc in documents])

    payload = {
        "vectorizer": vectorizer,
        "matrix": matrix,
        "documents": documents,
    }

    RAG_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RAG_INDEX_PATH.open("wb") as f:
        pickle.dump(payload, f)

    return RAG_INDEX_PATH

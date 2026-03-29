from __future__ import annotations

def rerank_chunks(chunks: list, query: str) -> list:
    query_tokens = set(query.lower().split())
    scored: list[tuple[float, RetrievedChunk]] = []
    for chunk in chunks:
        overlap = len(query_tokens.intersection(set(chunk.content.lower().split())))
        boosted = chunk.score + (overlap * 0.001)
        scored.append((boosted, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored]

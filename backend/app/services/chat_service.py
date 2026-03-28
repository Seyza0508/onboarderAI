from __future__ import annotations

from app.db.models import User
from app.rag.retriever import RetrievedChunk, retrieve_chunks


def answer_onboarding_question(user: User, question: str) -> tuple[str, list[str]]:
    retrieved = retrieve_chunks(question, top_k=4)
    if not retrieved:
        fallback = (
            f"I could not find a direct match in the onboarding documents for your question yet. "
            f"Based on your context ({user.role} on {user.team}), start with the onboarding handbook, "
            "then check who-to-contact guidance for owner routing."
        )
        return fallback, ["engineering_onboarding_handbook.md", "who_to_contact.md"]

    source_titles = _unique_sources(retrieved)
    bullets = _extract_actionable_points(retrieved)
    role_hint = f"For your role ({user.role}) and team ({user.team}), prioritize these next actions:"
    response = role_hint + "\n" + "\n".join(f"- {line}" for line in bullets)
    return response, source_titles


def _unique_sources(chunks: list[RetrievedChunk]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for chunk in chunks:
        if chunk.source in seen:
            continue
        seen.add(chunk.source)
        ordered.append(chunk.source)
    return ordered


def _extract_actionable_points(chunks: list[RetrievedChunk]) -> list[str]:
    points: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        lines = [ln.strip("- ").strip() for ln in chunk.content.splitlines() if ln.strip()]
        for line in lines:
            if line.startswith("#"):
                continue
            if len(line) < 30:
                continue
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            points.append(line)
            if len(points) >= 4:
                return points
    if not points:
        points.append("Review the referenced onboarding guides and follow the documented setup sequence.")
    return points

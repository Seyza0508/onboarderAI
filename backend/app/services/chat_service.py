from __future__ import annotations

from app.db.models import User
from app.llm.client import LlmClient
from app.rag.retriever import RetrievedChunk, retrieve_chunks


def answer_onboarding_question(
    user: User,
    question: str,
    provider_name: str = "mock",
    model_name: str = "mock-v1",
    api_key: str | None = None,
) -> tuple[str, list[str], float, str]:
    retrieved = retrieve_chunks(question, top_k=4)
    confidence = _compute_confidence(retrieved)
    if not retrieved:
        fallback = (
            f"I could not find a direct match in the onboarding documents for your question yet. "
            f"Based on your context ({user.role} on {user.team}), start with the onboarding handbook, "
            "then check who-to-contact guidance for owner routing."
        )
        return fallback, ["engineering_onboarding_handbook.md", "who_to_contact.md"], 0.0, "fallback"

    source_titles = _unique_sources(retrieved)
    bullets = _extract_actionable_points(retrieved)
    role_hint = f"User context: role={user.role}, team={user.team}."
    evidence = "\n".join(f"- {line}" for line in bullets)
    system_prompt = "You are an onboarding assistant. Keep advice concise and grounded in provided evidence."
    user_prompt = (
        f"{role_hint}\nQuestion: {question}\nGrounded evidence:\n{evidence}\n"
        "Produce a practical next-action response and mention if escalation is needed."
    )

    if confidence < 0.08:
        response = (
            "Evidence confidence is low for this question. Start with handbook and contact-directory guidance, "
            "then ask a mentor for confirmation."
        )
        return response, source_titles, confidence, "fallback_low_confidence"

    llm = LlmClient(provider_name=provider_name, model_name=model_name, api_key=api_key)
    synthesized = llm.generate(system_prompt=system_prompt, user_prompt=user_prompt)
    return synthesized, source_titles, confidence, llm.model_name


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


def _compute_confidence(chunks: list[RetrievedChunk]) -> float:
    if not chunks:
        return 0.0
    top_scores = [chunk.score for chunk in chunks[:3]]
    return float(sum(top_scores) / len(top_scores))

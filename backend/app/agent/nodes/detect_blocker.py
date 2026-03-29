from __future__ import annotations

from app.agent.state import WorkflowState


def run(state: WorkflowState) -> dict:
    text = str(state.payload.get("message", "")).lower()
    detected = any(keyword in text for keyword in ("blocked", "cannot", "can't", "access", "failed"))
    return {"detected_blocker": detected}

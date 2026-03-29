from __future__ import annotations

from app.agent.state import WorkflowState


def run(state: WorkflowState) -> dict:
    text = str(state.payload.get("message", "")).lower()
    if "access" in text or "repo" in text or "permission" in text:
        blocker_type = "access"
    elif "docker" in text or "run locally" in text or "dependency" in text:
        blocker_type = "environment"
    else:
        blocker_type = "dependency"
    return {"blocker_type": blocker_type}

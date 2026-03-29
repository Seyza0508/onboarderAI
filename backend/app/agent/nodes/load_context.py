from __future__ import annotations

from app.agent.state import WorkflowState


def run(state: WorkflowState) -> dict:
    state.context["loaded"] = True
    return {"loaded": True, "user_id": state.user_id}

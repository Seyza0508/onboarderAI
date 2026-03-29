from __future__ import annotations

from app.agent.state import WorkflowState


def run(state: WorkflowState) -> dict:
    return {"handoff_required": bool(state.payload.get("handoff_required", False))}

from __future__ import annotations

from app.agent.state import WorkflowState


def run(state: WorkflowState) -> dict:
    return {"planned": True, "message": "Plan node executed"}

from __future__ import annotations

from app.agent.state import WorkflowState


def run(state: WorkflowState) -> dict:
    return {"answer": state.payload.get("message", "No message provided")}

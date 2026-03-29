from __future__ import annotations

from app.agent.state import WorkflowState


def run(state: WorkflowState) -> dict:
    recommendation = state.outputs.get("recommend_next_action", {}).get("recommended_action", "Need escalation help")
    message = (
        "Hello team, I need assistance with an onboarding blocker. "
        f"Current recommendation: {recommendation}"
    )
    return {"draft_message": message}

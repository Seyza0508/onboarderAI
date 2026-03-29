from __future__ import annotations

from app.agent.state import WorkflowState


def run(state: WorkflowState) -> dict:
    blocker_type = state.outputs.get("classify_blocker", {}).get("blocker_type", "dependency")
    action_map = {
        "access": "Contact Developer Productivity and include role/team/start date.",
        "environment": "Run troubleshooting checklist and share error logs.",
        "documentation": "Ask onboarding channel for latest doc link and clarification.",
        "dependency": "Follow up with owning team and continue alternate tasks.",
        "ownership": "Escalate owner discovery to onboarding coordinator.",
    }
    return {"recommended_action": action_map.get(blocker_type, action_map["dependency"])}

from __future__ import annotations

from app.agent.state import WorkflowState


def run(state: WorkflowState) -> dict:
    return {
        "alternate_tasks": [
            "Read architecture overview",
            "Review onboarding handbook",
            "Prepare questions for mentor sync",
        ]
    }

from __future__ import annotations

from dataclasses import dataclass

from app.data_access.structured_loader import get_blocker_playbooks


@dataclass
class BlockerDecision:
    blocker_type: str
    classification_reason: str
    recommended_action: str
    alternate_tasks: list[str]
    escalation_needed: bool


def classify_blocker(
    description: str,
    severity: str,
    explicit_blocker_type: str | None = None,
    explicit_recommended_action: str | None = None,
    explicit_escalation_needed: bool | None = None,
) -> BlockerDecision:
    playbooks = get_blocker_playbooks()
    if explicit_blocker_type and explicit_blocker_type in playbooks:
        selected_type = explicit_blocker_type
    else:
        selected_type = _infer_blocker_type(description=description, playbooks=playbooks)

    playbook = playbooks[selected_type]
    recommended_action = explicit_recommended_action or playbook["recommended_action"]
    escalation_needed = (
        explicit_escalation_needed
        if explicit_escalation_needed is not None
        else _default_escalation(selected_type=selected_type, severity=severity)
    )

    return BlockerDecision(
        blocker_type=selected_type,
        classification_reason=playbook["why"],
        recommended_action=recommended_action,
        alternate_tasks=list(playbook.get("alternate_tasks", [])),
        escalation_needed=escalation_needed,
    )


def get_alternate_tasks_for_blocker_type(blocker_type: str) -> list[str]:
    playbooks = get_blocker_playbooks()
    playbook = playbooks.get(blocker_type)
    if not playbook:
        return []
    return list(playbook.get("alternate_tasks", []))


def _infer_blocker_type(description: str, playbooks: dict[str, dict]) -> str:
    text = description.lower()
    best_type = "dependency"
    best_score = 0

    for blocker_type, playbook in playbooks.items():
        score = 0
        for hint in playbook.get("detection_hints", []):
            if hint.lower() in text:
                score += 1
        if score > best_score:
            best_type = blocker_type
            best_score = score

    return best_type


def _default_escalation(selected_type: str, severity: str) -> bool:
    if severity in {"high", "critical"}:
        return True
    return selected_type in {"access", "ownership"}

from __future__ import annotations

from dataclasses import dataclass

from app.data_access.structured_loader import get_blocker_playbooks, get_contact_directory
from app.db.models import Blocker, User


@dataclass
class EscalationDraftResult:
    recipient_team: str
    recipient_owner: str
    destination: str
    message: str


def build_escalation_draft(
    user: User,
    blocker: Blocker,
    channel: str,
    what_tried: list[str] | None = None,
    help_needed: str | None = None,
) -> EscalationDraftResult:
    contact = _resolve_contact(blocker.blocker_type)
    destination = contact["slack_channel"] if channel == "slack" else contact["email"]

    tried_lines = what_tried or [
        "Reviewed relevant onboarding documentation",
        "Attempted standard troubleshooting steps",
    ]
    tried_text = "; ".join(tried_lines)
    requested_help = help_needed or blocker.recommended_action or "guidance on next steps and owner routing"

    if channel == "slack":
        message = (
            f"Hi @{contact['owner_name']}, I need help with an onboarding blocker.\n"
            f"- New hire: {user.name} ({user.role}, {user.team})\n"
            f"- Blocker type: {blocker.blocker_type}\n"
            f"- Issue: {blocker.description}\n"
            f"- What I tried: {tried_text}\n"
            f"- Help needed: {requested_help}\n"
            "Could you please advise on the next step or route me to the right owner?"
        )
    else:
        message = (
            f"Subject: Onboarding blocker escalation - {user.name} - {blocker.blocker_type}\n\n"
            f"Hello {contact['owner_name']},\n\n"
            f"I am {user.name} ({user.role} on {user.team}) and I am blocked during onboarding.\n\n"
            f"Blocker type: {blocker.blocker_type}\n"
            f"Issue details: {blocker.description}\n"
            f"What I tried: {tried_text}\n"
            f"Help needed: {requested_help}\n\n"
            "Please advise on resolution steps or redirect me to the correct owner.\n\n"
            "Thank you."
        )

    return EscalationDraftResult(
        recipient_team=contact["team"],
        recipient_owner=contact["owner_name"],
        destination=destination,
        message=message,
    )


def _resolve_contact(blocker_type: str) -> dict:
    playbooks = get_blocker_playbooks()
    contacts = get_contact_directory()

    preferred_team = playbooks.get(blocker_type, {}).get("default_escalation_team", "engineering_onboarding")
    if preferred_team in contacts:
        return contacts[preferred_team]

    return contacts["engineering_onboarding"]

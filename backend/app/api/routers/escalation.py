from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Blocker, Interaction, User
from app.db.schemas import EscalationDraftRequest, EscalationDraftResponse


router = APIRouter()


@router.post("/users/{user_id}/escalation-draft", response_model=EscalationDraftResponse, status_code=status.HTTP_200_OK)
def create_escalation_draft(
    user_id: int, payload: EscalationDraftRequest, db: Session = Depends(get_db)
) -> EscalationDraftResponse:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    blocker = None
    if payload.blocker_id is not None:
        blocker = db.get(Blocker, payload.blocker_id)
        if not blocker or blocker.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blocker not found for user")
    else:
        blocker = db.scalar(
            select(Blocker).where(Blocker.user_id == user_id, Blocker.status != "resolved").order_by(Blocker.created_at.desc())
        )

    if not blocker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No blocker available to draft escalation")

    draft_message = (
        f"Hello team, I am {user.name} ({user.role} on {user.team}) and I am currently blocked.\n"
        f"Blocker type: {blocker.blocker_type}\n"
        f"Issue: {blocker.description}\n"
        "What I tried: reviewed onboarding docs and attempted standard troubleshooting steps.\n"
        f"Help needed: {blocker.recommended_action or 'guidance on next steps and owner routing'}.\n"
        "Thank you."
    )

    interaction = Interaction(
        user_id=user_id,
        interaction_type="escalation",
        user_message=f"Draft {payload.channel} escalation",
        assistant_summary=f"Drafted escalation for blocker {blocker.id}",
    )
    db.add(interaction)
    db.commit()

    return EscalationDraftResponse(
        user_id=user_id,
        blocker_id=blocker.id,
        channel=payload.channel,
        draft_message=draft_message,
    )

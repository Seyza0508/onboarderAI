from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Blocker, Interaction, User
from app.db.schemas import EscalationDraftRequest, EscalationDraftResponse
from app.services.escalation_service import build_escalation_draft


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

    draft = build_escalation_draft(
        user=user,
        blocker=blocker,
        channel=payload.channel,
        what_tried=payload.what_tried,
        help_needed=payload.help_needed,
    )

    interaction = Interaction(
        user_id=user_id,
        interaction_type="escalation",
        user_message=f"Draft {payload.channel} escalation",
        assistant_summary=(
            f"Drafted {payload.channel} escalation for blocker {blocker.id} "
            f"to {draft.recipient_team} ({draft.recipient_owner})"
        ),
    )
    db.add(interaction)
    db.commit()

    return EscalationDraftResponse(
        user_id=user_id,
        blocker_id=blocker.id,
        channel=payload.channel,
        recipient_team=draft.recipient_team,
        recipient_owner=draft.recipient_owner,
        destination=draft.destination,
        draft_message=draft.message,
    )

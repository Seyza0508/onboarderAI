from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Blocker, Interaction, Task, User
from app.db.schemas import BlockerCreate, BlockerRead
from app.services.blocker_service import classify_blocker


router = APIRouter()


@router.post("/users/{user_id}/blockers", response_model=BlockerRead, status_code=status.HTTP_201_CREATED)
def create_blocker(user_id: int, payload: BlockerCreate, db: Session = Depends(get_db)) -> BlockerRead:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.task_id is not None:
        task = db.get(Task, payload.task_id)
        if not task or task.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found for user")
        task.status = "blocked"

    decision = classify_blocker(
        description=payload.description,
        severity=payload.severity,
        explicit_blocker_type=payload.blocker_type,
        explicit_recommended_action=payload.recommended_action,
        explicit_escalation_needed=payload.escalation_needed,
    )

    blocker = Blocker(
        user_id=user_id,
        task_id=payload.task_id,
        blocker_type=decision.blocker_type,
        description=payload.description,
        severity=payload.severity,
        status=payload.status,
        recommended_action=decision.recommended_action,
        escalation_needed=decision.escalation_needed,
    )
    db.add(blocker)

    interaction = Interaction(
        user_id=user_id,
        interaction_type="blocker",
        user_message=payload.description,
        assistant_summary=(
            f"Classified blocker as {decision.blocker_type}. "
            f"Why: {decision.classification_reason}. "
            f"Recommended action: {decision.recommended_action}"
        ),
    )
    db.add(interaction)
    db.commit()
    db.refresh(blocker)
    return BlockerRead(
        id=blocker.id,
        user_id=blocker.user_id,
        task_id=blocker.task_id,
        blocker_type=blocker.blocker_type,
        description=blocker.description,
        severity=blocker.severity,
        status=blocker.status,
        recommended_action=blocker.recommended_action,
        escalation_needed=blocker.escalation_needed,
        classification_reason=decision.classification_reason,
        alternate_tasks=decision.alternate_tasks,
        created_at=blocker.created_at,
        updated_at=blocker.updated_at,
    )

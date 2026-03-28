from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Blocker, Interaction, Task, User
from app.db.schemas import BlockerCreate, BlockerRead


router = APIRouter()


@router.post("/users/{user_id}/blockers", response_model=BlockerRead, status_code=status.HTTP_201_CREATED)
def create_blocker(user_id: int, payload: BlockerCreate, db: Session = Depends(get_db)) -> Blocker:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.task_id is not None:
        task = db.get(Task, payload.task_id)
        if not task or task.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found for user")
        task.status = "blocked"

    blocker = Blocker(
        user_id=user_id,
        task_id=payload.task_id,
        blocker_type=payload.blocker_type,
        description=payload.description,
        severity=payload.severity,
        status=payload.status,
        recommended_action=payload.recommended_action,
        escalation_needed=payload.escalation_needed,
    )
    db.add(blocker)

    interaction = Interaction(
        user_id=user_id,
        interaction_type="blocker",
        user_message=payload.description,
        assistant_summary=f"Logged {payload.blocker_type} blocker for user {user_id}",
    )
    db.add(interaction)
    db.commit()
    db.refresh(blocker)
    return blocker

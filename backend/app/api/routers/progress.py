from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Blocker, Task, User
from app.db.schemas import ProgressResponse


router = APIRouter()


@router.get("/users/{user_id}/progress", response_model=ProgressResponse, status_code=status.HTTP_200_OK)
def get_progress(user_id: int, db: Session = Depends(get_db)) -> ProgressResponse:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    total_tasks = db.scalar(select(func.count(Task.id)).where(Task.user_id == user_id)) or 0
    completed_tasks = db.scalar(
        select(func.count(Task.id)).where(Task.user_id == user_id, Task.status == "complete")
    ) or 0
    blocked_tasks = db.scalar(select(func.count(Task.id)).where(Task.user_id == user_id, Task.status == "blocked")) or 0
    pending_tasks = max(total_tasks - completed_tasks - blocked_tasks, 0)

    current_blocker = db.scalar(
        select(Blocker)
        .where(Blocker.user_id == user_id, Blocker.status != "resolved")
        .order_by(Blocker.created_at.desc())
    )
    recommended_next_action = current_blocker.recommended_action if current_blocker else None

    return ProgressResponse(
        user_id=user_id,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        blocked_tasks=blocked_tasks,
        pending_tasks=pending_tasks,
        current_blocker=current_blocker,
        recommended_next_action=recommended_next_action,
    )

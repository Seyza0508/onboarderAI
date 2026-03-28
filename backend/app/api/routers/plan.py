from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Interaction, Task, User
from app.db.schemas import PlanGenerateResponse, TaskRead
from app.services.plan_service import generate_tasks_for_user


router = APIRouter()


@router.post("/users/{user_id}/plan/generate", response_model=PlanGenerateResponse, status_code=status.HTTP_200_OK)
def generate_plan(user_id: int, db: Session = Depends(get_db)) -> PlanGenerateResponse:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing_tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()

    if existing_tasks:
        interaction = Interaction(
            user_id=user_id,
            interaction_type="plan",
            user_message="Generate onboarding plan",
            assistant_summary="Plan already exists; no new tasks generated",
        )
        db.add(interaction)
        db.commit()
        return PlanGenerateResponse(user_id=user_id, generated_task_count=0, message="Plan already exists for this user")

    generated_tasks = generate_tasks_for_user(user, db)

    interaction = Interaction(
        user_id=user_id,
        interaction_type="plan",
        user_message="Generate onboarding plan",
        assistant_summary=f"Generated {len(generated_tasks)} personalized onboarding tasks for {user.role} on {user.team}",
    )
    db.add(interaction)
    db.commit()

    return PlanGenerateResponse(
        user_id=user_id,
        generated_task_count=len(generated_tasks),
        message=f"Generated personalized onboarding plan for {user.role} on {user.team}",
    )


@router.get("/users/{user_id}/plan", response_model=list[TaskRead], status_code=status.HTTP_200_OK)
def get_plan(user_id: int, db: Session = Depends(get_db)) -> list[Task]:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    tasks = db.scalars(select(Task).where(Task.user_id == user_id).order_by(Task.created_at.asc())).all()
    return list(tasks)

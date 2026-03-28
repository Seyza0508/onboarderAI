from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Interaction, Task, User
from app.db.schemas import PlanGenerateResponse, TaskRead


router = APIRouter()


@router.post("/users/{user_id}/plan/generate", response_model=PlanGenerateResponse, status_code=status.HTTP_200_OK)
def generate_plan(user_id: int, db: Session = Depends(get_db)) -> PlanGenerateResponse:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing_tasks = db.scalars(select(Task).where(Task.user_id == user_id)).all()
    generated = 0

    if not existing_tasks:
        starter_tasks = [
            Task(
                user_id=user_id,
                task_name="Confirm core tool access for onboarding",
                category="access",
                status="not_started",
                priority="high",
                doc_reference="engineering_onboarding_handbook.md",
            ),
            Task(
                user_id=user_id,
                task_name="Review team onboarding documentation",
                category="architecture",
                status="not_started",
                priority="medium",
                doc_reference="payments_team_onboarding.md",
            ),
        ]
        db.add_all(starter_tasks)
        generated = len(starter_tasks)

    interaction = Interaction(
        user_id=user_id,
        interaction_type="plan",
        user_message="Generate onboarding plan",
        assistant_summary="Generated initial onboarding task plan",
    )
    db.add(interaction)
    db.commit()

    message = "Plan generated with starter tasks" if generated else "Plan already exists for this user"
    return PlanGenerateResponse(user_id=user_id, generated_task_count=generated, message=message)


@router.get("/users/{user_id}/plan", response_model=list[TaskRead], status_code=status.HTTP_200_OK)
def get_plan(user_id: int, db: Session = Depends(get_db)) -> list[Task]:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    tasks = db.scalars(select(Task).where(Task.user_id == user_id).order_by(Task.created_at.asc())).all()
    return list(tasks)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_db, get_user_in_org
from app.db.models import Blocker, Interaction, LlmProvider, Task
from app.db.schemas import BlockerCreate, BlockerRead
from app.llm.client import LlmClient
from app.services.blocker_service import classify_blocker


router = APIRouter()


@router.post("/users/{user_id}/blockers", response_model=BlockerRead, status_code=status.HTTP_201_CREATED)
def create_blocker(
    user_id: int,
    payload: BlockerCreate,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> BlockerRead:
    get_user_in_org(user_id=user_id, ctx=ctx, db=db)

    linked_task_id: int | None = payload.task_id
    if linked_task_id is not None:
        task = db.get(Task, linked_task_id)
        if not task or task.user_id != user_id or (
            task.organization_id is not None and task.organization_id != ctx.organization_id
        ):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found for user")
        task.status = "blocked"
    else:
        fallback_task = db.scalar(
            select(Task)
            .where(
                Task.user_id == user_id,
                Task.organization_id == ctx.organization_id,
                Task.status.in_(("not_started", "in_progress")),
            )
            .order_by(Task.created_at.asc())
        )
        if fallback_task:
            fallback_task.status = "blocked"
            linked_task_id = fallback_task.id

    decision = classify_blocker(
        description=payload.description,
        severity=payload.severity,
        explicit_blocker_type=payload.blocker_type,
        explicit_recommended_action=payload.recommended_action,
        explicit_escalation_needed=payload.escalation_needed,
    )

    blocker = Blocker(
        organization_id=ctx.organization_id,
        user_id=user_id,
        task_id=linked_task_id,
        blocker_type=decision.blocker_type,
        description=payload.description,
        severity=payload.severity,
        status=payload.status,
        recommended_action=decision.recommended_action,
        escalation_needed=decision.escalation_needed,
    )
    db.add(blocker)

    interaction = Interaction(
        organization_id=ctx.organization_id,
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


@router.post("/users/{user_id}/blockers/{blocker_id}/explain", status_code=status.HTTP_200_OK)
def explain_blocker(
    user_id: int,
    blocker_id: int,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> dict:
    get_user_in_org(user_id=user_id, ctx=ctx, db=db)
    blocker = db.get(Blocker, blocker_id)
    if not blocker or blocker.user_id != user_id or blocker.organization_id != ctx.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blocker not found")

    provider = db.scalar(
        select(LlmProvider).where(LlmProvider.organization_id == ctx.organization_id, LlmProvider.is_default.is_(True))
    )
    provider_name = provider.provider_name if provider else "mock"
    model_name = provider.model_name if provider else "mock-v1"
    llm = LlmClient(provider_name=provider_name, model_name=model_name)
    explanation = llm.generate(
        system_prompt="Explain blocker root cause and next action concisely.",
        user_prompt=(
            f"Blocker type: {blocker.blocker_type}\n"
            f"Severity: {blocker.severity}\n"
            f"Description: {blocker.description}\n"
            f"Recommended action: {blocker.recommended_action or 'N/A'}"
        ),
    )
    return {"blocker_id": blocker.id, "explanation": explanation, "model_used": llm.model_name}

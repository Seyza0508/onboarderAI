from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_db
from app.db.models import HumanHandoff, WorkflowRun, WorkflowStep
from app.services.workflow_service import run_workflow


router = APIRouter()


class WorkflowPayload(BaseModel):
    payload: dict = {}


def _start_workflow(
    workflow_type: str,
    user_id: int,
    payload: WorkflowPayload,
    db: Session,
    ctx: AuthContext,
) -> dict:
    if ctx.organization_id <= 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid organization context")
    run = run_workflow(
        db=db,
        organization_id=ctx.organization_id,
        user_id=user_id,
        workflow_type=workflow_type,
        payload=payload.payload,
    )
    return {"run_id": run.id, "status": run.status, "workflow_type": run.workflow_type}


@router.post("/users/{user_id}/workflows/onboarding-run", status_code=status.HTTP_200_OK)
def onboarding_run(
    user_id: int,
    payload: WorkflowPayload,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> dict:
    return _start_workflow("onboarding-run", user_id, payload, db, ctx)


@router.post("/users/{user_id}/workflows/question-run", status_code=status.HTTP_200_OK)
def question_run(
    user_id: int,
    payload: WorkflowPayload,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> dict:
    return _start_workflow("question-run", user_id, payload, db, ctx)


@router.post("/users/{user_id}/workflows/blocker-run", status_code=status.HTTP_200_OK)
def blocker_run(
    user_id: int,
    payload: WorkflowPayload,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> dict:
    return _start_workflow("blocker-run", user_id, payload, db, ctx)


@router.get("/workflows/{run_id}", status_code=status.HTTP_200_OK)
def get_workflow(run_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)) -> dict:
    run = db.get(WorkflowRun, run_id)
    if not run or run.organization_id != ctx.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow run not found")
    steps = db.scalars(select(WorkflowStep).where(WorkflowStep.workflow_run_id == run_id)).all()
    return {
        "run": {
            "id": run.id,
            "status": run.status,
            "workflow_type": run.workflow_type,
            "started_at": run.started_at,
            "ended_at": run.ended_at,
        },
        "steps": [{"node_name": step.node_name, "status": step.status, "output": step.output_payload} for step in steps],
    }


@router.post("/workflows/{run_id}/handoff", status_code=status.HTTP_200_OK)
def create_handoff(
    run_id: int,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> dict:
    run = db.get(WorkflowRun, run_id)
    if not run or run.organization_id != ctx.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow run not found")
    handoff = HumanHandoff(
        workflow_run_id=run_id,
        owner_user_id=None,
        reason="Manual handoff requested",
        status="open",
    )
    run.status = "requires_handoff"
    db.add(handoff)
    db.commit()
    db.refresh(handoff)
    return {"handoff_id": handoff.id, "status": handoff.status}

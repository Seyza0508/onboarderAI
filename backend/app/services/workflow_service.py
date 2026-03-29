from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.agent.graph import execute_flow
from app.agent.state import WorkflowState
from app.db.models import HumanHandoff, WorkflowRun, WorkflowStep


def run_workflow(
    db: Session,
    organization_id: int,
    user_id: int,
    workflow_type: str,
    payload: dict | None = None,
) -> WorkflowRun:
    run = WorkflowRun(
        organization_id=organization_id,
        user_id=user_id,
        workflow_type=workflow_type,
        status="running",
    )
    db.add(run)
    db.flush()

    state = WorkflowState(
        organization_id=organization_id,
        user_id=user_id,
        workflow_type=workflow_type,
        payload=payload or {},
    )
    outputs = execute_flow(state)

    for node_name, output in outputs.items():
        db.add(
            WorkflowStep(
                workflow_run_id=run.id,
                node_name=node_name,
                input_payload=payload or {},
                output_payload=output,
                status="success",
            )
        )

    handoff_result = outputs.get("handoff_to_human", {})
    if handoff_result.get("handoff_required"):
        db.add(
            HumanHandoff(
                workflow_run_id=run.id,
                owner_user_id=None,
                reason="Workflow requested human handoff",
                status="open",
            )
        )
        run.status = "requires_handoff"
    else:
        run.status = "completed"
    run.ended_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    return run

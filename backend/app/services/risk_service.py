from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Blocker, Interaction, RiskScore, Task, User


def compute_user_risk(db: Session, user: User) -> RiskScore:
    total_tasks = db.scalar(select(func.count(Task.id)).where(Task.user_id == user.id)) or 0
    completed_tasks = db.scalar(select(func.count(Task.id)).where(Task.user_id == user.id, Task.status == "complete")) or 0
    open_blockers = db.scalar(select(func.count(Blocker.id)).where(Blocker.user_id == user.id, Blocker.status != "resolved")) or 0
    high_blockers = db.scalar(
        select(func.count(Blocker.id)).where(
            Blocker.user_id == user.id,
            Blocker.status != "resolved",
            Blocker.severity.in_(("high", "critical")),
        )
    ) or 0
    escalation_count = db.scalar(
        select(func.count(Interaction.id)).where(Interaction.user_id == user.id, Interaction.interaction_type == "escalation")
    ) or 0

    days_since_start = max((date.today() - user.start_date).days, 0)
    completion_ratio = (completed_tasks / total_tasks) if total_tasks else 0.0
    stagnant_penalty = 10.0 if completion_ratio < 0.2 and days_since_start > 3 else 0.0
    score = (
        open_blockers * 15.0
        + high_blockers * 20.0
        + escalation_count * 8.0
        + max(0.0, (1.0 - completion_ratio) * 30.0)
        + stagnant_penalty
    )

    if score >= 70:
        risk_level = "high"
    elif score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"

    risk = RiskScore(
        user_id=user.id,
        organization_id=user.organization_id or 0,
        score=score,
        risk_level=risk_level,
        factors_json={
            "open_blockers": open_blockers,
            "high_blockers": high_blockers,
            "days_since_start": days_since_start,
            "completion_ratio": completion_ratio,
            "escalation_count": escalation_count,
        },
    )
    db.add(risk)
    db.commit()
    db.refresh(risk)
    return risk

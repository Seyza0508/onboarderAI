from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Blocker, RiskScore, Task, Team, User


def organization_dashboard(db: Session, organization_id: int) -> dict:
    total_users = db.scalar(select(func.count(User.id)).where(User.organization_id == organization_id)) or 0
    active_blockers = db.scalar(
        select(func.count(Blocker.id)).where(Blocker.organization_id == organization_id, Blocker.status != "resolved")
    ) or 0
    high_blockers = db.scalar(
        select(func.count(Blocker.id)).where(
            Blocker.organization_id == organization_id,
            Blocker.status != "resolved",
            Blocker.severity.in_(("high", "critical")),
        )
    ) or 0
    completed_tasks = db.scalar(
        select(func.count(Task.id)).where(Task.organization_id == organization_id, Task.status == "complete")
    ) or 0
    total_tasks = db.scalar(select(func.count(Task.id)).where(Task.organization_id == organization_id)) or 0
    completion_rate = (completed_tasks / total_tasks) if total_tasks else 0.0

    return {
        "organization_id": organization_id,
        "active_new_hires": total_users,
        "active_blockers": active_blockers,
        "high_severity_blockers": high_blockers,
        "completion_rate": completion_rate,
    }


def organization_blocker_breakdown(db: Session, organization_id: int) -> list[dict]:
    rows = db.execute(
        select(Blocker.blocker_type, func.count(Blocker.id))
        .where(Blocker.organization_id == organization_id, Blocker.status != "resolved")
        .group_by(Blocker.blocker_type)
    ).all()
    return [{"blocker_type": blocker_type, "count": count} for blocker_type, count in rows]


def team_dashboard(db: Session, team_id: int) -> dict:
    team = db.get(Team, team_id)
    if not team:
        return {"team_id": team_id, "members": 0, "at_risk": 0}
    users = db.scalars(select(User).where(User.organization_id == team.organization_id, User.team == team.name)).all()
    user_ids = [u.id for u in users]
    at_risk = 0
    if user_ids:
        at_risk = db.scalar(
            select(func.count(RiskScore.id)).where(RiskScore.user_id.in_(user_ids), RiskScore.risk_level == "high")
        ) or 0
    return {"team_id": team_id, "team_name": team.name, "members": len(user_ids), "at_risk": at_risk}

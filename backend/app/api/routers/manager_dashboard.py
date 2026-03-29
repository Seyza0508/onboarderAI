from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_db
from app.services.dashboard_service import organization_blocker_breakdown, organization_dashboard, team_dashboard


router = APIRouter()


def _ensure_manager(ctx: AuthContext) -> None:
    if ctx.role not in {"admin", "manager"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager access required")


@router.get("/organizations/{org_id}/dashboard", status_code=status.HTTP_200_OK)
def get_organization_dashboard(
    org_id: int,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> dict:
    _ensure_manager(ctx)
    if ctx.organization_id != org_id and ctx.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return organization_dashboard(db=db, organization_id=org_id)


@router.get("/organizations/{org_id}/dashboard/blockers", status_code=status.HTTP_200_OK)
def get_organization_blockers(
    org_id: int,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> list[dict]:
    _ensure_manager(ctx)
    if ctx.organization_id != org_id and ctx.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return organization_blocker_breakdown(db=db, organization_id=org_id)


@router.get("/teams/{team_id}/dashboard", status_code=status.HTTP_200_OK)
def get_team_dashboard(
    team_id: int,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> dict:
    _ensure_manager(ctx)
    return team_dashboard(db=db, team_id=team_id)

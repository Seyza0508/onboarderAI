from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_db
from app.db.models import RiskScore, User
from app.services.risk_service import compute_user_risk


router = APIRouter()


@router.get("/users/{user_id}/risk", status_code=status.HTTP_200_OK)
def get_user_risk(
    user_id: int,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> dict:
    user = db.get(User, user_id)
    if not user or user.organization_id != ctx.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    latest = db.scalar(select(RiskScore).where(RiskScore.user_id == user_id).order_by(RiskScore.created_at.desc()))
    if latest is None:
        latest = compute_user_risk(db=db, user=user)
    return {
        "user_id": user_id,
        "score": latest.score,
        "risk_level": latest.risk_level,
        "factors": latest.factors_json,
    }


@router.post("/users/{user_id}/risk/recompute", status_code=status.HTTP_200_OK)
def recompute_user_risk(
    user_id: int,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> dict:
    user = db.get(User, user_id)
    if not user or user.organization_id != ctx.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    score = compute_user_risk(db=db, user=user)
    return {"user_id": user_id, "score": score.score, "risk_level": score.risk_level, "factors": score.factors_json}

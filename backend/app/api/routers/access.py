from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import User, UserAccessStatus
from app.db.schemas import UserAccessCreate, UserAccessRead


router = APIRouter()


@router.post("/users/{user_id}/access", response_model=UserAccessRead, status_code=status.HTTP_201_CREATED)
def upsert_user_access(user_id: int, payload: UserAccessCreate, db: Session = Depends(get_db)) -> UserAccessStatus:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = db.scalar(
        select(UserAccessStatus).where(
            UserAccessStatus.user_id == user_id,
            UserAccessStatus.tool_name == payload.tool_name.strip().lower(),
        )
    )

    if existing:
        existing.status = payload.status
        existing.notes = payload.notes
        db.commit()
        db.refresh(existing)
        return existing

    access = UserAccessStatus(
        user_id=user_id,
        tool_name=payload.tool_name.strip().lower(),
        status=payload.status,
        notes=payload.notes,
    )
    db.add(access)
    db.commit()
    db.refresh(access)
    return access

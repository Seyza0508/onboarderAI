from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_db, get_user_in_org
from app.db.models import User, UserAccessStatus
from app.db.schemas import UserAccessCreate, UserAccessRead


router = APIRouter()


@router.get("/users/{user_id}/access", response_model=list[UserAccessRead], status_code=status.HTTP_200_OK)
def list_user_access(
    user_id: int,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> list[UserAccessStatus]:
    get_user_in_org(user_id=user_id, ctx=ctx, db=db)

    rows = db.scalars(
        select(UserAccessStatus).where(UserAccessStatus.user_id == user_id).order_by(UserAccessStatus.tool_name)
    ).all()
    return list(rows)


@router.post("/users/{user_id}/access", response_model=UserAccessRead, status_code=status.HTTP_201_CREATED)
def upsert_user_access(
    user_id: int,
    payload: UserAccessCreate,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> UserAccessStatus:
    get_user_in_org(user_id=user_id, ctx=ctx, db=db)

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

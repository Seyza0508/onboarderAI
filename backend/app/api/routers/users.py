from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import User
from app.db.schemas import UserCreate, UserRead


router = APIRouter()


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    user = User(
        name=payload.name.strip(),
        email=payload.email.strip().lower(),
        role=payload.role.strip(),
        team=payload.team.strip(),
        level=payload.level.strip(),
        manager_name=payload.manager_name.strip(),
        start_date=payload.start_date,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

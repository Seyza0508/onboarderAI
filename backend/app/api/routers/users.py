from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.data_access.structured_loader import get_role_requirements
from app.db.models import User, UserAccessStatus
from app.db.schemas import UserCreate, UserDetailRead, UserRead


router = APIRouter()


@router.post("/users", response_model=UserDetailRead, status_code=status.HTTP_201_CREATED)
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
    db.flush()

    role_reqs = get_role_requirements()
    role_entry = role_reqs.get(user.role)
    if role_entry:
        for tool_name in role_entry["required_tools"]:
            access = UserAccessStatus(
                user_id=user.id,
                tool_name=tool_name,
                status="not_requested",
            )
            db.add(access)

    db.commit()
    db.refresh(user)
    return user


@router.get("/users/{user_id}", response_model=UserDetailRead, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

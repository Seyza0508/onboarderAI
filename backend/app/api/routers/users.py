from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_db, get_user_in_org
from app.data_access.structured_loader import get_role_requirements
from app.db.models import OrganizationMembership, User, UserAccessStatus
from app.db.schemas import UserCreate, UserDetailRead, UserRead


router = APIRouter()


@router.post("/users", response_model=UserDetailRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> User:
    existing = db.scalar(select(User).where(User.email == payload.email, User.organization_id == ctx.organization_id))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    user = User(
        organization_id=ctx.organization_id,
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

    existing_membership = db.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.organization_id == ctx.organization_id,
            OrganizationMembership.user_id == user.id,
        )
    )
    if existing_membership is None:
        db.add(OrganizationMembership(organization_id=ctx.organization_id, user_id=user.id, role=payload.role))

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
def get_user(user_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)) -> User:
    return get_user_in_org(user_id=user_id, ctx=ctx, db=db)

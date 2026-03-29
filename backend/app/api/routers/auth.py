from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import Account, Organization, OrganizationMembership, User


router = APIRouter(prefix="/auth")


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=8)
    organization_name: str
    organization_slug: str
    role: str = "new_hire"
    team: str = "general"
    level: str = "mid"
    manager_name: str = "TBD"
    start_date: date = date.today()


class LoginRequest(BaseModel):
    email: str
    password: str
    organization_slug: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    organization_id: int
    role: str


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> AuthResponse:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    org = db.scalar(select(Organization).where(Organization.slug == payload.organization_slug))
    if org is None:
        org = Organization(name=payload.organization_name.strip(), slug=payload.organization_slug.strip().lower())
        db.add(org)
        db.flush()

    user = User(
        organization_id=org.id,
        name=payload.name.strip(),
        email=payload.email.strip().lower(),
        role=payload.role,
        team=payload.team,
        level=payload.level,
        manager_name=payload.manager_name,
        start_date=payload.start_date,
    )
    db.add(user)
    db.flush()

    db.add(Account(user_id=user.id, password_hash=hash_password(payload.password)))
    db.add(OrganizationMembership(organization_id=org.id, user_id=user.id, role=payload.role))
    db.commit()

    token = create_access_token(
        subject=str(user.id),
        extra={"organization_id": org.id, "role": payload.role},
    )
    return AuthResponse(access_token=token, user_id=user.id, organization_id=org.id, role=payload.role)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    org = db.scalar(select(Organization).where(Organization.slug == payload.organization_slug.strip().lower()))
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    user = db.scalar(
        select(User).where(
            User.email == payload.email.strip().lower(),
            User.organization_id == org.id,
        )
    )
    if not user or not user.account:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_password(payload.password, user.account.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    membership = db.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.user_id == user.id,
            OrganizationMembership.organization_id == org.id,
        )
    )
    role = membership.role if membership else user.role
    token = create_access_token(subject=str(user.id), extra={"organization_id": org.id, "role": role})
    return AuthResponse(access_token=token, user_id=user.id, organization_id=org.id, role=role)

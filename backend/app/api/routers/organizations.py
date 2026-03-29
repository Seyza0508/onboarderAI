from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context, get_db, require_role
from app.db.models import LlmProvider, Organization, OrganizationMembership, Team, User


router = APIRouter()


class OrganizationCreate(BaseModel):
    name: str
    slug: str


class OrganizationRead(BaseModel):
    id: int
    name: str
    slug: str


class MemberCreate(BaseModel):
    user_id: int
    role: str


class TeamCreate(BaseModel):
    name: str
    manager_user_id: int | None = None


class LlmConfigRequest(BaseModel):
    provider_name: str
    model_name: str
    api_key_encrypted: str | None = None
    is_default: bool = True


@router.post("/organizations", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_role("admin")),
) -> Organization:
    if db.scalar(select(Organization).where(Organization.slug == payload.slug.strip().lower())):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slug already exists")
    org = Organization(name=payload.name.strip(), slug=payload.slug.strip().lower())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/organizations/{org_id}", response_model=OrganizationRead)
def get_organization(org_id: int, db: Session = Depends(get_db), ctx: AuthContext = Depends(get_auth_context)) -> Organization:
    if org_id != ctx.organization_id and ctx.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org


@router.post("/organizations/{org_id}/members", status_code=status.HTTP_201_CREATED)
def add_member(
    org_id: int,
    payload: MemberCreate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_role("admin", "manager")),
) -> dict:
    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.organization_id != org_id:
        user.organization_id = org_id
    membership = db.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.organization_id == org_id,
            OrganizationMembership.user_id == payload.user_id,
        )
    )
    if membership:
        membership.role = payload.role
    else:
        db.add(OrganizationMembership(organization_id=org_id, user_id=payload.user_id, role=payload.role))
    db.commit()
    return {"status": "ok"}


@router.get("/organizations/{org_id}/members")
def list_members(
    org_id: int,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_role("admin", "manager")),
) -> list[dict]:
    memberships = db.scalars(select(OrganizationMembership).where(OrganizationMembership.organization_id == org_id)).all()
    out: list[dict] = []
    for item in memberships:
        user = db.get(User, item.user_id)
        if user:
            out.append({"user_id": user.id, "name": user.name, "email": user.email, "role": item.role})
    return out


@router.post("/organizations/{org_id}/teams", status_code=status.HTTP_201_CREATED)
def create_team(
    org_id: int,
    payload: TeamCreate,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_role("admin", "manager")),
) -> dict:
    team = Team(organization_id=org_id, name=payload.name.strip(), manager_user_id=payload.manager_user_id)
    db.add(team)
    db.commit()
    db.refresh(team)
    return {"id": team.id, "name": team.name}


@router.get("/organizations/{org_id}/teams")
def list_teams(
    org_id: int,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> list[dict]:
    if ctx.organization_id != org_id and ctx.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    teams = db.scalars(select(Team).where(Team.organization_id == org_id)).all()
    return [{"id": t.id, "name": t.name, "manager_user_id": t.manager_user_id} for t in teams]


@router.post("/organizations/{org_id}/llm/config", status_code=status.HTTP_201_CREATED)
def set_llm_config(
    org_id: int,
    payload: LlmConfigRequest,
    db: Session = Depends(get_db),
    _: AuthContext = Depends(require_role("admin")),
) -> dict:
    provider_name = payload.provider_name.strip().lower()
    if provider_name not in {"mock", "openai", "anthropic"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="provider_name must be one of: mock, openai, anthropic",
        )
    if payload.is_default:
        default_rows = db.scalars(select(LlmProvider).where(LlmProvider.organization_id == org_id)).all()
        for row in default_rows:
            row.is_default = False
    provider = LlmProvider(
        organization_id=org_id,
        provider_name=provider_name,
        model_name=payload.model_name.strip(),
        api_key_encrypted=(payload.api_key_encrypted.strip() if payload.api_key_encrypted else None),
        is_default=payload.is_default,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return {"id": provider.id, "provider_name": provider.provider_name, "model_name": provider.model_name}


@router.get("/organizations/{org_id}/llm/config")
def get_llm_config(
    org_id: int,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> list[dict]:
    if ctx.organization_id != org_id and ctx.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    rows = db.scalars(select(LlmProvider).where(LlmProvider.organization_id == org_id)).all()
    return [
        {"id": row.id, "provider_name": row.provider_name, "model_name": row.model_name, "is_default": row.is_default}
        for row in rows
    ]

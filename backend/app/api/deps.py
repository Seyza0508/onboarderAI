from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.models import OrganizationMembership, User
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


@dataclass
class AuthContext:
    user_id: int
    organization_id: int
    role: str


def get_auth_context(
    db: Session = Depends(get_db),
    token: str | None = Depends(oauth2_scheme),
    x_user_id: int | None = Header(default=None),
    x_org_id: int | None = Header(default=None),
) -> AuthContext:
    if token:
        payload = decode_token(token)
        user_id = int(payload["sub"])
        organization_id = int(payload["organization_id"])
        role = str(payload.get("role", "new_hire"))
        return AuthContext(user_id=user_id, organization_id=organization_id, role=role)

    if x_user_id and x_org_id:
        membership = db.scalar(
            select(OrganizationMembership).where(
                OrganizationMembership.user_id == x_user_id,
                OrganizationMembership.organization_id == x_org_id,
            )
        )
        if not membership:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid dev auth headers")
        return AuthContext(user_id=x_user_id, organization_id=x_org_id, role=membership.role)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")


def require_role(*roles: str):
    def _checker(ctx: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if ctx.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return ctx

    return _checker


def get_user_in_org(user_id: int, ctx: AuthContext, db: Session) -> User:
    user = db.get(User, user_id)
    if not user or user.organization_id != ctx.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


__all__ = ["get_db", "get_auth_context", "require_role", "AuthContext", "get_user_in_org"]

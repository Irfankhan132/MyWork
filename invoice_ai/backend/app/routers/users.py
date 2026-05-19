from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from app.core.db import get_db
from app.core.auth import get_context, RequestContext
from app.models.user import User
from app.models.tenant_member import TenantMember
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate, ctx: RequestContext = Depends(get_context), db: Session = Depends(get_db)):
    # Only allow owner/admin to add users
    if ctx.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Only owner/admin can add users")

    tenant_id = ctx.tenant_id

    user = User(
        id=uuid4(),
        email=payload.email,
        tenant_id=tenant_id,
    )
    db.add(user)
    db.flush()

    existing_members = (
        db.query(TenantMember)
        .filter(TenantMember.tenant_id == tenant_id)
        .count()
    )
    # If tenant already has members, new users should be member
    role = "owner" if existing_members == 0 else "member"

    membership = TenantMember(
        tenant_id=tenant_id,
        user_id=user.id,
        role=role,
    )
    db.add(membership)

    db.commit()

    return UserResponse(
        id=user.id,
        email=user.email,
        tenant_id=tenant_id,
        role=role,
    )

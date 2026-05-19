from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.db import get_db
from app.models.user import User
from app.models.tenant_member import TenantMember


class RequestContext:
    def __init__(self, user: User, tenant_id: UUID, role: str):
        self.user = user
        self.tenant_id = tenant_id
        self.role = role


def get_context(
    x_user_id: str = Header(..., alias="X-User-Id"),
    x_tenant_id: str = Header(..., alias="X-Tenant-Id"),
    db: Session = Depends(get_db),
) -> RequestContext:
    try:
        user_id = UUID(x_user_id)
        tenant_id = UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id or X-Tenant-Id UUID")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Unknown user")

    membership = (
        db.query(TenantMember)
        .filter(TenantMember.user_id == user_id, TenantMember.tenant_id == tenant_id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="User is not a member of this tenant")

    return RequestContext(user=user, tenant_id=tenant_id, role=membership.role)

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import get_context, RequestContext
from app.core.db import get_db
from app.models.tenant import Tenant
from app.models.tenant_member import TenantMember
from app.models.user import User

router = APIRouter(prefix="/tenants", tags=["tenants"])


class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)


class TenantBootstrap(BaseModel):
    tenant_name: str = Field(min_length=2, max_length=200)
    owner_email: EmailStr


@router.post("", status_code=201)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db)):
    tenant = Tenant(name=payload.name.strip())
    db.add(tenant)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tenant name already exists")

    db.refresh(tenant)
    return {"id": str(tenant.id), "name": tenant.name, "created_at": tenant.created_at}


@router.get("/mine")
def list_my_tenants(ctx: RequestContext = Depends(get_context), db: Session = Depends(get_db)):
    rows = (
        db.query(Tenant.id, Tenant.name, TenantMember.role)
        .join(TenantMember, TenantMember.tenant_id == Tenant.id)
        .filter(TenantMember.user_id == ctx.user.id)
        .all()
    )

    return [{"id": str(tid), "name": name, "role": role} for (tid, name, role) in rows]


@router.post("/bootstrap", status_code=201)
def bootstrap_tenant(payload: TenantBootstrap, db: Session = Depends(get_db)):
    # 1) Create tenant
    tenant = Tenant(name=payload.tenant_name.strip())
    db.add(tenant)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tenant name already exists")
    db.refresh(tenant)

    # 2) Create owner user
    owner = User(
        id=uuid4(),
        email=payload.owner_email.strip().lower(),
        tenant_id=tenant.id,
    )
    db.add(owner)
    db.flush()

    # 3) Create membership as owner
    membership = TenantMember(
        tenant_id=tenant.id,
        user_id=owner.id,
        role="owner",
    )
    db.add(membership)
    db.commit()

    return {
        "tenant_id": str(tenant.id),
        "tenant_name": tenant.name,
        "owner_user_id": str(owner.id),
        "owner_email": owner.email,
        "role": "owner",
    }

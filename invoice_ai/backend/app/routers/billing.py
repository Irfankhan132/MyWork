from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.core.db import get_db
from app.core.auth import get_context, RequestContext
from app.models.billing_account import BillingAccount

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/me")
def billing_me(ctx: RequestContext = Depends(get_context), db: Session = Depends(get_db)):
    acct = db.query(BillingAccount).filter(BillingAccount.user_id == ctx.user.id).first()

    # If user has no billing row yet, treat as free
    if not acct:
        return {
            "user_id": str(ctx.user.id),
            "is_paid": False,
            "plan": "free",
        }

    return {
        "user_id": str(acct.user_id),
        "is_paid": acct.is_paid,
        "plan": acct.plan,
        "created_at": acct.created_at,
        "updated_at": acct.updated_at,
    }


@router.post("/upgrade")
def billing_upgrade(ctx: RequestContext = Depends(get_context), db: Session = Depends(get_db)):
    # UPSERT (create if missing)
    stmt = (
        insert(BillingAccount)
        .values(user_id=ctx.user.id, is_paid=True, plan="pro")
        .on_conflict_do_update(
            index_elements=[BillingAccount.user_id],
            set_=dict(is_paid=True, plan="pro"),
        )
        .returning(BillingAccount.user_id, BillingAccount.is_paid, BillingAccount.plan)
    )

    row = db.execute(stmt).first()
    db.commit()

    return {
        "user_id": str(row.user_id),
        "is_paid": row.is_paid,
        "plan": row.plan,
        "message": "Upgraded (sandbox).",
    }


@router.post("/downgrade")
def billing_downgrade(ctx: RequestContext = Depends(get_context), db: Session = Depends(get_db)):
    stmt = (
        insert(BillingAccount)
        .values(user_id=ctx.user.id, is_paid=False, plan="free")
        .on_conflict_do_update(
            index_elements=[BillingAccount.user_id],
            set_=dict(is_paid=False, plan="free"),
        )
        .returning(BillingAccount.user_id, BillingAccount.is_paid, BillingAccount.plan)
    )

    row = db.execute(stmt).first()
    db.commit()

    return {
        "user_id": str(row.user_id),
        "is_paid": row.is_paid,
        "plan": row.plan,
        "message": "Downgraded (sandbox).",
    }

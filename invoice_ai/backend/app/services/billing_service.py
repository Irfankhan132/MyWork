from sqlalchemy.orm import Session
from app.models.billing_account import BillingAccount


def get_or_create_billing_account(db: Session, user_id):
    acct = db.query(BillingAccount).filter(BillingAccount.user_id == user_id).first()
    if acct:
        return acct

    acct = BillingAccount(user_id=user_id, is_paid=False, plan="free")
    db.add(acct)
    db.commit()
    db.refresh(acct)
    return acct


def is_user_paid(db: Session, user_id) -> bool:
    acct = get_or_create_billing_account(db, user_id)
    return bool(acct.is_paid)

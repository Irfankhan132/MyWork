from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timezone, date

from app.core.auth import get_context, RequestContext
from app.core.db import get_db
from app.models.invoice import Invoice
from app.services.token_service import consume_tokens, estimate_tokens_for_text
from app.services.provider_router import select_provider


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatAsk(BaseModel):
    question: str = Field(min_length=2, max_length=500)


def _month_range(d: date):
    start = date(d.year, d.month, 1)
    if d.month == 12:
        end = date(d.year + 1, 1, 1)
    else:
        end = date(d.year, d.month + 1, 1)
    return start, end


@router.post("/ask")
def ask(
    payload: ChatAsk,
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
):
    q = payload.question.strip().lower()
    
    
    # Token charging (mock estimation)
    # Later we will estimate tokens properly from prompt+response.
    tokens = estimate_tokens_for_text(payload.question)

    endpoint = "chat.ask"
    provider_id = select_provider(
        db,
        user_id=str(ctx.user.id),
        endpoint=endpoint,
        preferred_provider="gemini",
    )

    charge = consume_tokens(
        db,
        user_id=ctx.user.id,
        tenant_id=ctx.tenant_id,
        endpoint=endpoint,
        tokens=tokens,
        provider_id="gemini",
    )


    if charge.get("exhausted_all"):
        raise HTTPException(
            status_code=402,
            detail="Daily free quota exhausted. Please upgrade to continue."
        )

    
    

    now = datetime.now(timezone.utc)
    start_today = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    start_month, end_month = _month_range(now.date())

    # 1) How many invoices today?
    if "how many" in q and "today" in q and "invoice" in q:
        count_today = db.query(func.count()).filter(
            Invoice.tenant_id == ctx.tenant_id,
            Invoice.created_at >= start_today,
        ).scalar()
        return {
            "intent": "invoices_today",
            "answer": f"You have {int(count_today or 0)} invoices today.",
            "data": {"invoices_today": int(count_today or 0)},
            "billing": charge,

        }

    # 2) Show risky invoices
    if "risky" in q or "risk" in q:
        # Allow user to ask "risky >= 80" etc (optional)
        # Default threshold = 50
        min_score = 50
        for token in q.split():
            if token.isdigit():
                min_score = int(token)
                break
        min_score = max(0, min(100, min_score))

        rows = db.query(Invoice).filter(
            Invoice.tenant_id == ctx.tenant_id,
            Invoice.risk_score.isnot(None),
            Invoice.risk_score >= min_score,
        ).order_by(desc(Invoice.risk_score), desc(Invoice.created_at)).limit(20).all()

        # Summarize flags
        flag_counts: dict[str, int] = {}
        for r in rows:
            rf = r.risk_flags or {}
            flags = rf.get("flags", []) if isinstance(rf, dict) else []
            for f in flags:
                flag_counts[f] = flag_counts.get(f, 0) + 1

        return {
            "intent": "risky_invoices",
            "answer": f"Found {len(rows)} risky invoices (risk_score >= {min_score}).",
            "summary": {
                "min_score": min_score,
                "flag_counts": flag_counts,
            },
            "data": [
                {
                    "id": str(r.id),
                    "vendor": r.vendor,
                    "invoice_number": r.invoice_number,
                    "total": float(r.total) if r.total is not None else None,
                    "risk_score": r.risk_score,
                    "risk_flags": r.risk_flags,
                    "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ],
        }


    # 3) Top vendors by spend (this month)
    if "top vendor" in q or ("vendor" in q and "spend" in q):
        top = db.query(
            Invoice.vendor,
            func.coalesce(func.sum(Invoice.total), 0).label("spend"),
            func.count().label("count"),
        ).filter(
            Invoice.tenant_id == ctx.tenant_id,
            Invoice.created_at >= start_month,
            Invoice.created_at < end_month,
            Invoice.vendor.isnot(None),
        ).group_by(Invoice.vendor).order_by(desc("spend")).limit(5).all()

        return {
            "intent": "top_vendors_month",
            "answer": "Here are the top vendors by spend for this month.",
            "data": [
                {"vendor": v, "spend": float(s), "count": int(c)}
                for (v, s, c) in top
            ],
        }

    # 4) Monthly report
    if "monthly" in q and ("report" in q or "summary" in q):
        count_total = db.query(func.count()).filter(
            Invoice.tenant_id == ctx.tenant_id,
            Invoice.created_at >= start_month,
            Invoice.created_at < end_month,
        ).scalar()

        sums = db.query(
            func.coalesce(func.sum(Invoice.total), 0),
            func.coalesce(func.sum(Invoice.tax), 0),
        ).filter(
            Invoice.tenant_id == ctx.tenant_id,
            Invoice.created_at >= start_month,
            Invoice.created_at < end_month,
        ).first()

        total_sum, tax_sum = sums

        return {
            "intent": "monthly_report",
            "answer": f"Monthly totals: {float(total_sum or 0)} total, {float(tax_sum or 0)} tax.",
            "data": {
                "month": f"{now.year:04d}-{now.month:02d}",
                "count_total": int(count_total or 0),
                "total_sum": float(total_sum or 0),
                "tax_sum": float(tax_sum or 0),
            },
        }

    # fallback (unknown intent, but still bill tokens)
    return {
        "intent": "unknown",
        "answer": (
            "I don't understand yet. Try: "
            "'How many invoices today?', "
            "'Top vendors by spend', "
            "'Show risky invoices', "
            "'Generate monthly report'."
        ),
        "billing": charge,
    }


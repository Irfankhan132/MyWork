from datetime import datetime, date, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.auth import get_context, RequestContext
from app.core.db import get_db
from app.models.invoice import Invoice

router = APIRouter(prefix="/reports", tags=["reports"])


def _month_range(year: int, month: int):
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end


@router.get("/summary")
def summary(
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
):
    # "Today" in UTC for now (good enough). Later we can use tenant timezone.
    now = datetime.now(timezone.utc)
    start_today = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    q = db.query(Invoice).filter(
        Invoice.tenant_id == ctx.tenant_id,
        Invoice.created_at >= start_today,
    )

    invoices_today = q.count()

    totals = db.query(
        func.coalesce(func.sum(Invoice.total), 0),
        func.coalesce(func.sum(Invoice.tax), 0),
    ).filter(
        Invoice.tenant_id == ctx.tenant_id,
        Invoice.created_at >= start_today,
    ).first()

    total_sum, tax_sum = totals

    processed_today = db.query(func.count()).filter(
        Invoice.tenant_id == ctx.tenant_id,
        Invoice.created_at >= start_today,
        Invoice.status == "processed",
    ).scalar()

    risky_today = db.query(func.count()).filter(
        Invoice.tenant_id == ctx.tenant_id,
        Invoice.created_at >= start_today,
        Invoice.risk_score.isnot(None),
        Invoice.risk_score >= 50,
    ).scalar()

    return {
        "tenant_id": str(ctx.tenant_id),
        "today": start_today.isoformat(),
        "invoices_today": invoices_today,
        "processed_today": int(processed_today or 0),
        "risky_today": int(risky_today or 0),
        "total_sum_today": float(total_sum or 0),
        "tax_sum_today": float(tax_sum or 0),
    }


@router.get("/monthly")
def monthly(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
):
    start, end = _month_range(year, month)

    base = db.query(Invoice).filter(
        Invoice.tenant_id == ctx.tenant_id,
        Invoice.created_at >= start,
        Invoice.created_at < end,
    )

    count_total = base.count()

    sums = db.query(
        func.coalesce(func.sum(Invoice.total), 0),
        func.coalesce(func.sum(Invoice.tax), 0),
    ).filter(
        Invoice.tenant_id == ctx.tenant_id,
        Invoice.created_at >= start,
        Invoice.created_at < end,
    ).first()

    total_sum, tax_sum = sums

    # Top vendors by spend (ignore null vendor)
    top_vendors = db.query(
        Invoice.vendor,
        func.coalesce(func.sum(Invoice.total), 0).label("spend"),
        func.count().label("count"),
    ).filter(
        Invoice.tenant_id == ctx.tenant_id,
        Invoice.created_at >= start,
        Invoice.created_at < end,
        Invoice.vendor.isnot(None),
    ).group_by(Invoice.vendor).order_by(desc("spend")).limit(5).all()

    # Risk distribution
    risky_count = db.query(func.count()).filter(
        Invoice.tenant_id == ctx.tenant_id,
        Invoice.created_at >= start,
        Invoice.created_at < end,
        Invoice.risk_score.isnot(None),
        Invoice.risk_score >= 50,
    ).scalar()

    return {
        "tenant_id": str(ctx.tenant_id),
        "month": f"{year:04d}-{month:02d}",
        "count_total": count_total,
        "total_sum": float(total_sum or 0),
        "tax_sum": float(tax_sum or 0),
        "risky_count": int(risky_count or 0),
        "top_vendors": [
            {"vendor": v, "spend": float(s), "count": int(c)}
            for (v, s, c) in top_vendors
        ],
    }


@router.get("/risky")
def risky_invoices(
    min_score: int = Query(50, ge=0, le=100),
    limit: int = Query(20, ge=1, le=100),
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
):
    rows = db.query(Invoice).filter(
        Invoice.tenant_id == ctx.tenant_id,
        Invoice.risk_score.isnot(None),
        Invoice.risk_score >= min_score,
    ).order_by(desc(Invoice.risk_score), desc(Invoice.created_at)).limit(limit).all()

    return [
        {
            "id": str(r.id),
            "created_at": r.created_at.isoformat(),
            "vendor": r.vendor,
            "invoice_number": r.invoice_number,
            "total": float(r.total) if r.total is not None else None,
            "risk_score": r.risk_score,
            "risk_flags": r.risk_flags,
            "compliance_status": r.compliance_status,
            "status": r.status,
        }
        for r in rows
    ]

from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.core.db import get_db
from app.core.auth import get_context, RequestContext
from app.models.ai_usage_event import AIUsageEvent

router = APIRouter(prefix="/usage", tags=["usage"])


# -----------------------------
# Response models
# -----------------------------
class ProviderUsageRow(BaseModel):
    provider_id: str
    total_tokens: int
    free_tokens: int
    overage_tokens: int


class UsageTotals(BaseModel):
    total_tokens: int
    free_tokens: int
    overage_tokens: int


class UsageTodayResponse(BaseModel):
    tenant_id: str
    day_utc: str
    providers: list[ProviderUsageRow]
    totals: UsageTotals


class UsageMonthlyResponse(BaseModel):
    tenant_id: str
    month: str  # YYYY-MM
    providers: list[ProviderUsageRow]
    totals: UsageTotals


class UsageMonthlyMeResponse(UsageMonthlyResponse):
    user_id: str


class UsageTodayMeResponse(UsageTodayResponse):
    user_id: str


# -----------------------------
# Helpers
# -----------------------------
def _day_start_utc() -> datetime:
    return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)


def parse_month(month: str) -> tuple[datetime, datetime]:
    # month = "YYYY-MM"
    try:
        start = datetime.strptime(month, "%Y-%m").replace(tzinfo=timezone.utc)
    except ValueError:
        raise HTTPException(status_code=400, detail="month must be YYYY-MM")

    # next month boundary
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end


def _usage_query(
    db: Session,
    *,
    tenant_id,
    start: datetime,
    end: datetime | None = None,
    user_id=None,
    endpoint: str | None = None,
):
    q = (
        db.query(
            AIUsageEvent.provider_id.label("provider_id"),
            func.coalesce(func.sum(AIUsageEvent.tokens_used), 0).label("total_tokens"),
            func.coalesce(
                func.sum(
                    case(
                        (AIUsageEvent.is_overage == False, AIUsageEvent.tokens_used),
                        else_=0,
                    )
                ),
                0,
            ).label("free_tokens"),
            func.coalesce(
                func.sum(
                    case(
                        (AIUsageEvent.is_overage == True, AIUsageEvent.tokens_used),
                        else_=0,
                    )
                ),
                0,
            ).label("overage_tokens"),
        )
        .filter(AIUsageEvent.tenant_id == tenant_id)
        .filter(AIUsageEvent.created_at >= start)
    )

    if end is not None:
        q = q.filter(AIUsageEvent.created_at < end)

    if user_id is not None:
        q = q.filter(AIUsageEvent.user_id == user_id)

    if endpoint:
        q = q.filter(AIUsageEvent.endpoint == endpoint)

    return q.group_by(AIUsageEvent.provider_id).order_by(AIUsageEvent.provider_id)


def _rows_to_payload(rows) -> tuple[list[ProviderUsageRow], UsageTotals]:
    providers = [
        ProviderUsageRow(
            provider_id=r.provider_id,
            total_tokens=int(r.total_tokens),
            free_tokens=int(r.free_tokens),
            overage_tokens=int(r.overage_tokens),
        )
        for r in rows
    ]

    totals = UsageTotals(
        total_tokens=sum(p.total_tokens for p in providers),
        free_tokens=sum(p.free_tokens for p in providers),
        overage_tokens=sum(p.overage_tokens for p in providers),
    )

    return providers, totals


# -----------------------------
# Routes
# -----------------------------
@router.get("/today/providers", response_model=UsageTodayResponse)
def usage_today_by_provider(
    endpoint: str | None = None,  # optional filter, e.g. "invoice.process"
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
):
    start = _day_start_utc()

    rows = _usage_query(
        db,
        tenant_id=ctx.tenant_id,
        start=start,
        endpoint=endpoint,
    ).all()

    providers, totals = _rows_to_payload(rows)

    return UsageTodayResponse(
        tenant_id=str(ctx.tenant_id),
        day_utc=start.date().isoformat(),
        providers=providers,
        totals=totals,
    )


@router.get("/today/me", response_model=UsageTodayMeResponse)
def usage_today_me(
    endpoint: str | None = None,  # optional filter
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
):
    start = _day_start_utc()

    rows = _usage_query(
        db,
        tenant_id=ctx.tenant_id,
        user_id=ctx.user.id,
        start=start,
        endpoint=endpoint,
    ).all()

    providers, totals = _rows_to_payload(rows)

    return UsageTodayMeResponse(
        tenant_id=str(ctx.tenant_id),
        user_id=str(ctx.user.id),
        day_utc=start.date().isoformat(),
        providers=providers,
        totals=totals,
    )


@router.get("/monthly", response_model=UsageMonthlyResponse)
def usage_monthly_by_provider(
    month: str,  # "YYYY-MM"
    endpoint: str | None = None,  # optional filter
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
):
    start, end = parse_month(month)

    rows = _usage_query(
        db,
        tenant_id=ctx.tenant_id,
        start=start,
        end=end,
        endpoint=endpoint,
    ).all()

    providers, totals = _rows_to_payload(rows)

    return UsageMonthlyResponse(
        tenant_id=str(ctx.tenant_id),
        month=month,
        providers=providers,
        totals=totals,
    )


@router.get("/monthly/me", response_model=UsageMonthlyMeResponse)
def usage_monthly_me(
    month: str,
    endpoint: str | None = None,  # optional filter
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
):
    start, end = parse_month(month)

    rows = _usage_query(
        db,
        tenant_id=ctx.tenant_id,
        user_id=ctx.user.id,
        start=start,
        end=end,
        endpoint=endpoint,
    ).all()

    providers, totals = _rows_to_payload(rows)

    return UsageMonthlyMeResponse(
        tenant_id=str(ctx.tenant_id),
        user_id=str(ctx.user.id),
        month=month,
        providers=providers,
        totals=totals,
    )

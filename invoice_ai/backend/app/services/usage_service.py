from __future__ import annotations

from datetime import datetime, timezone, date
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.ai_usage_event import AIUsageEvent


def get_today_usage(db: Session, tenant_id, user_id=None):
    # today in UTC
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start.replace(hour=23, minute=59, second=59, microsecond=999999)

    q = db.query(
        AIUsageEvent.provider_id.label("provider_id"),
        func.coalesce(func.sum(AIUsageEvent.tokens_used), 0).label("total_tokens"),
        func.coalesce(func.sum(case((AIUsageEvent.is_overage == False, AIUsageEvent.tokens_used), else_=0)), 0).label("free_tokens"),
        func.coalesce(func.sum(case((AIUsageEvent.is_overage == True, AIUsageEvent.tokens_used), else_=0)), 0).label("overage_tokens"),
        func.count(AIUsageEvent.id).label("events_count"),
    ).filter(
        AIUsageEvent.tenant_id == tenant_id,
        AIUsageEvent.created_at >= start,
        AIUsageEvent.created_at <= end,
    )

    if user_id:
        q = q.filter(AIUsageEvent.user_id == user_id)

    rows = q.group_by(AIUsageEvent.provider_id).order_by(AIUsageEvent.provider_id).all()

    # overall totals
    total_tokens = sum(r.total_tokens for r in rows)
    free_tokens = sum(r.free_tokens for r in rows)
    overage_tokens = sum(r.overage_tokens for r in rows)

    return {
        "date_utc": str(start.date()),
        "tenant_id": str(tenant_id),
        "user_id": str(user_id) if user_id else None,
        "totals": {
            "total_tokens": int(total_tokens),
            "free_tokens": int(free_tokens),
            "overage_tokens": int(overage_tokens),
        },
        "by_provider": [
            {
                "provider_id": r.provider_id,
                "total_tokens": int(r.total_tokens),
                "free_tokens": int(r.free_tokens),
                "overage_tokens": int(r.overage_tokens),
                "events_count": int(r.events_count),
            }
            for r in rows
        ],
    }

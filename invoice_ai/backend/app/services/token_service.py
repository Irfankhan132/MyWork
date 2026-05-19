from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.ai_usage_event import AIUsageEvent
# from app.core.config import PROVIDER_PRIORITY, OVERAGE_UNIT_PRICE_MICROS, OVERAGE_CURRENCY
from app.services.billing_service import is_user_paid          
from app.core.config import settings

from typing import List

from app.models.daily_token_quota import DailyTokenQuota  



DEFAULT_FREE_QUOTA_PER_PROVIDER = 1000

def estimate_tokens_for_text(text: str) -> int:
    # very simple estimator: ~1 token per 4 characters (rough approximation)
    text = (text or "").strip()
    estimated = max(20, int(len(text) / 4))
    return min(400, estimated)  # cap to avoid crazy values



DEFAULT_FREE_QUOTA_PER_PROVIDER = 1000

def ensure_daily_quotas(db: Session, user_id, tenant_id, day: date | None = None) -> list[DailyTokenQuota]:
    day = day or date.today()

    quotas: list[DailyTokenQuota] = []
    for provider_id in settings.PROVIDER_PRIORITY:
        q = (
            db.query(DailyTokenQuota)
            .filter(DailyTokenQuota.user_id == user_id)
            .filter(DailyTokenQuota.tenant_id == tenant_id)   # ✅ NEW
            .filter(DailyTokenQuota.day == day)
            .filter(DailyTokenQuota.provider_id == provider_id)
            .one_or_none()
        )

        if not q:
            q = DailyTokenQuota(
                id=uuid4(),
                user_id=user_id,
                tenant_id=tenant_id,                          # ✅ NEW
                day=day,
                provider_id=provider_id,
                free_quota=DEFAULT_FREE_QUOTA_PER_PROVIDER,
                used_tokens=0,
            )
            db.add(q)

        quotas.append(q)

    db.flush()
    return quotas





def get_today_usage(db: Session, user_id) -> list[dict]:
    """Return today's quotas with remaining tokens per provider."""
    day = date.today()
    quotas = ensure_daily_quotas(db, user_id, day)

    out = []
    for q in quotas:
        remaining = max(0, (q.free_quota or 0) - (q.used_tokens or 0))
        out.append(
            {
                "provider_id": q.provider_id,
                "day": q.day.isoformat(),
                "free_quota": q.free_quota,
                "used_tokens": q.used_tokens,
                "remaining_tokens": remaining,
            }
        )
    return out



def consume_tokens(
    db: Session,
    *,
    user_id: str,
    tenant_id: str,
    endpoint: str,
    tokens: int,
    provider_id: str | None = None,
) -> dict:
    if tokens <= 0:
        raise ValueError("tokens must be > 0")

    day = date.today()
    quotas = ensure_daily_quotas(db, user_id, tenant_id, day)

    # Sort so the ACTUAL provider used is charged first (if provided)
    provider_priority = list(settings.PROVIDER_PRIORITY or [])
    priority_index = {pid: i for i, pid in enumerate(provider_priority)}

    # force chosen provider to the front (only if provider_id was provided)
    if provider_id:
        priority_index[provider_id] = -1

    quotas = sorted(quotas, key=lambda q: priority_index.get(q.provider_id, 999))

    remaining_to_charge = int(tokens)
    charges: list[dict] = []

    # pricing config
    price_map = settings.OVERAGE_UNIT_PRICE_MICROS or {}
    currency = settings.OVERAGE_CURRENCY

    # 1) consume free quota(s)
    for q in quotas:
        if remaining_to_charge <= 0:
            break

        remaining = int((q.free_quota or 0) - (q.used_tokens or 0))
        if remaining <= 0:
            continue

        charge = min(remaining_to_charge, remaining)
        q.used_tokens = int((q.used_tokens or 0) + charge)

        # free usage event
        db.add(
            AIUsageEvent(
                id=uuid4(),
                user_id=user_id,
                tenant_id=tenant_id,
                provider_id=q.provider_id,
                endpoint=endpoint,
                tokens_used=int(charge),
                is_overage=False,
                cost_micros=0,
                currency=currency,
            )
        )
        db.flush()

        charges.append(
            {
                "provider_id": q.provider_id,
                "charged_tokens": int(charge),
                "remaining_after": int(max(0, (q.free_quota or 0) - (q.used_tokens or 0))),
                "is_overage": False,
                "cost_micros": 0,
                "currency": currency,
            }
        )

        remaining_to_charge -= int(charge)

    # 2) handle exhausted
    paid_user = is_user_paid(db, user_id)

    if remaining_to_charge > 0:
        if not paid_user:
            db.rollback()
            raise HTTPException(
                status_code=402,
                detail="Daily free quota exhausted. Please upgrade to continue.",
            )

        # Paid user: record overage on actual provider (fallback if missing)
        overage_provider = provider_id or (provider_priority[0] if provider_priority else "gemini")
        overage_tokens = int(remaining_to_charge)

        unit_price_micros = int(price_map.get(overage_provider, 0))
        cost_micros = int(overage_tokens * unit_price_micros)

        db.add(
            AIUsageEvent(
                id=uuid4(),
                user_id=user_id,
                tenant_id=tenant_id,
                provider_id=overage_provider,
                endpoint=endpoint,
                tokens_used=overage_tokens,
                is_overage=True,
                cost_micros=cost_micros,
                currency=currency,
            )
        )
        db.flush()

        charges.append(
            {
                "provider_id": overage_provider,
                "charged_tokens": overage_tokens,
                "is_overage": True,
                "unit_price_micros": unit_price_micros,
                "cost_micros": cost_micros,
                "currency": currency,
                "note": "Paid user: overage recorded (provider-specific)",
            }
        )

        remaining_to_charge = 0

    db.commit()

    return {
        "requested_tokens": int(tokens),
        "charged_total": int(tokens),
        "exhausted_all": False,
        "charges": charges,
    }

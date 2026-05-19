from __future__ import annotations

from datetime import date
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.token_service import ensure_daily_quotas  # same function you already have


def select_provider(
    db: Session,
    *,
    user_id: str,
    endpoint: str,
    preferred_provider: str | None = None,
    day: date | None = None,
) -> str:
    """
    Provider selection strategy:

    1) If preferred_provider is passed and it's in priority -> try it first if it has free quota left
    2) Otherwise choose first provider (by settings.PROVIDER_PRIORITY) that still has free quota remaining
    3) If none has free quota:
        - if paid user later -> overage allowed; pick cheapest configured provider (or fall back to priority[0])
        - if free user later -> consume_tokens will raise 402 anyway
    """
    day = day or date.today()

    priority = list(settings.PROVIDER_PRIORITY or [])
    if not priority:
        # fallback hard-stop, but keep a safe default
        return preferred_provider or "gemini"

    quotas = ensure_daily_quotas(db, user_id, day)

    # Map provider -> remaining free tokens
    remaining_map: dict[str, int] = {}
    for q in quotas:
        remaining = int((q.free_quota or 0) - (q.used_tokens or 0))
        remaining_map[q.provider_id] = remaining

    def has_free(p: str) -> bool:
        return int(remaining_map.get(p, 0)) > 0

    # 1) try preferred first (if valid + has free)
    if preferred_provider and preferred_provider in priority and has_free(preferred_provider):
        return preferred_provider

    # 2) pick first provider in priority with free tokens left
    for p in priority:
        if has_free(p):
            return p

    # 3) none has free quota: pick cheapest provider for overage (paid users),
    # or just return priority[0] (free users will get 402 in consume_tokens)
    price_map = settings.OVERAGE_UNIT_PRICE_MICROS or {}
    cheapest = None
    cheapest_price = None
    for p in priority:
        price = price_map.get(p)
        if price is None:
            continue
        if cheapest_price is None or int(price) < int(cheapest_price):
            cheapest = p
            cheapest_price = int(price)

    return cheapest or priority[0]

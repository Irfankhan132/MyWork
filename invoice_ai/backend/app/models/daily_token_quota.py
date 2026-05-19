import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base  # adjust if your Base is elsewhere


class DailyTokenQuota(Base):
    __tablename__ = "daily_token_quotas"
    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", "provider_id", "day", name="uq_tenant_user_provider_day"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)  # ✅ NEW

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider_id: Mapped[str] = mapped_column(ForeignKey("ai_providers.id"), nullable=False)

    day: Mapped[date] = mapped_column(Date, nullable=False)

    free_quota: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    used_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

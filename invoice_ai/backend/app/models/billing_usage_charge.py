from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.db import Base

class BillingUsageCharge(Base):
    __tablename__ = "billing_usage_charges"

    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    provider_id = Column(String, nullable=False)
    ai_usage_event_id = Column(UUID(as_uuid=True), ForeignKey("ai_usage_events.id"), nullable=False, unique=True)

    tokens = Column(Integer, nullable=False)
    unit_price_micros = Column(Integer, nullable=False)
    amount_micros = Column(BigInteger, nullable=False)

    currency = Column(String, nullable=False, default="EUR")
    status = Column(String, nullable=False, default="pending")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

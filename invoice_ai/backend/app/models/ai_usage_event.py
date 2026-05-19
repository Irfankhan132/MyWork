import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.db import Base

from sqlalchemy import Column, Boolean, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import BigInteger, String


class AIUsageEvent(Base):
    __tablename__ = "ai_usage_events"
    
    is_overage = Column(Boolean, nullable=False, default=False, server_default="false")

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    provider_id: Mapped[str] = mapped_column(ForeignKey("ai_providers.id"), nullable=False)

    endpoint: Mapped[str] = mapped_column(String(100), nullable=False)  # "chat.ask", "invoice.process"
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False)
    
    cost_micros = Column(BigInteger, nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="EUR")
    


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    
    

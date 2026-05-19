import uuid
from sqlalchemy import Date, DateTime, Numeric, String, Text, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from sqlalchemy import Integer


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    # File info (we'll populate after upload step)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=True)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=True)

    # Extracted fields (initially null; filled by OCR/AI later)
    vendor: Mapped[str] = mapped_column(String(255), nullable=True)
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=True)
    invoice_date: Mapped[Date] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=True)

    subtotal: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=True)
    tax: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=True)
    total: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="uploaded")
    extracted_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    invoice_type: Mapped[str] = mapped_column(String(50), nullable=True)
    language: Mapped[str] = mapped_column(String(20), nullable=True)

    risk_score: Mapped[int] = mapped_column(Integer, nullable=True)
    risk_flags: Mapped[dict] = mapped_column(JSONB, nullable=True)

    compliance_status: Mapped[str] = mapped_column(String(20), nullable=True)

    agent_results: Mapped[dict] = mapped_column(JSONB, nullable=True)

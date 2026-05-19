from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from datetime import date
from typing import Any


class InvoiceResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    filename: str
    content_type: str | None = None
    status: str
    created_at: datetime



class InvoiceDetail(BaseModel):
    id: UUID
    tenant_id: UUID
    filename: str
    content_type: str | None = None
    storage_path: str | None = None

    vendor: str | None = None
    invoice_number: str | None = None
    invoice_date: date | None = None
    currency: str | None = None
    subtotal: float | None = None
    tax: float | None = None
    total: float | None = None

    status: str
    extracted_data: dict[str, Any] | None = None
    notes: str | None = None

    created_at: datetime


class InvoiceUpdate(BaseModel):
    vendor: str | None = None
    invoice_number: str | None = None
    invoice_date: date | None = None
    currency: str | None = None
    subtotal: float | None = None
    tax: float | None = None
    total: float | None = None
    notes: str | None = None

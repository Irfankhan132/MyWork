from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
from pathlib import Path


@dataclass
class ExtractedInvoice:
    vendor: str | None = None
    invoice_number: str | None = None
    invoice_date: date | None = None
    currency: str | None = None
    subtotal: float | None = None
    tax: float | None = None
    total: float | None = None
    raw: dict | None = None


def _guess_currency(text: str) -> str | None:
    # Very small heuristic for demo
    if "€" in text or "EUR" in text.upper():
        return "EUR"
    if "$" in text or "USD" in text.upper():
        return "USD"
    if "SAR" in text.upper():
        return "SAR"
    return None


def extract_from_file(storage_path: str) -> ExtractedInvoice:
    """
    MOCK extraction:
    - If it's a .txt, parse it a bit (useful for testing).
    - Otherwise return reasonable demo values.
    """
    path = Path(storage_path)
    raw = {"source": "mock_ocr_agent", "file": path.name}

    # If user uploads .txt, we can parse it to look more realistic
    if path.suffix.lower() == ".txt" and path.exists():
        text = path.read_text(encoding="utf-8", errors="ignore")
        raw["text_preview"] = text[:500]

        currency = _guess_currency(text)

        inv_no = None
        m = re.search(r"(invoice\s*#|invoice\s*no\.?|inv\s*#)\s*([A-Za-z0-9\-]+)", text, re.IGNORECASE)
        if m:
            inv_no = m.group(2)

        total = None
        m = re.search(r"(total)\s*[:=]?\s*([0-9]+(?:\.[0-9]{1,2})?)", text, re.IGNORECASE)
        if m:
            total = float(m.group(2))

        vendor = None
        m = re.search(r"(vendor|supplier)\s*[:=]?\s*(.+)", text, re.IGNORECASE)
        if m:
            vendor = m.group(2).strip()[:255]

        return ExtractedInvoice(
            vendor=vendor or "Demo Vendor GmbH",
            invoice_number=inv_no or "INV-DEMO-001",
            invoice_date=date.today(),
            currency=currency or "EUR",
            subtotal=None,
            tax=None,
            total=total or 119.00,
            raw=raw,
        )

    # Non-txt files: return defaults
    return ExtractedInvoice(
        vendor="Demo Vendor GmbH",
        invoice_number="INV-DEMO-001",
        invoice_date=date.today(),
        currency="EUR",
        subtotal=100.00,
        tax=19.00,
        total=119.00,
        raw=raw,
    )

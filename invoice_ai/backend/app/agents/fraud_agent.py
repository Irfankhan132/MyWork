from __future__ import annotations
from dataclasses import dataclass


@dataclass
class FraudResult:
    risk_score: int
    flags: list[str]
    details: dict


def fraud_check(
    duplicate_invoice_number: bool,
    suspicious_similarity: bool,
    total: float | None,
    vendor: str | None,
    invoice_number: str | None,
) -> FraudResult:
    score = 0
    flags: list[str] = []

    # Missing fields
    if not invoice_number:
        score += 10
        flags.append("missing_invoice_number")
    if not vendor:
        score += 10
        flags.append("missing_vendor")
    if total is None:
        score += 15
        flags.append("missing_total")

    # Duplicate invoice number
    if duplicate_invoice_number:
        score += 60
        flags.append("duplicate_invoice_number")

    # Similar invoice (vendor+total close in time)
    if suspicious_similarity:
        score += 35
        flags.append("similar_vendor_total_recently")

    # Amount-based anomaly
    if total is not None and total > 10000:
        score += 40
        flags.append("high_amount")

    # Clamp 0..100
    score = max(0, min(100, score))

    return FraudResult(
        risk_score=score,
        flags=flags,
        details={
            "duplicate_invoice_number": duplicate_invoice_number,
            "suspicious_similarity": suspicious_similarity,
            "total": total,
            "vendor": vendor,
        },
    )

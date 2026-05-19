from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ComplianceResult:
    status: str   # pass/warn/fail
    details: dict


def check_compliance(currency: str | None, tax: float | None) -> ComplianceResult:
    # Very simple rules (expand later)
    if currency is None:
        return ComplianceResult(status="warn", details={"reason": "missing_currency"})

    if currency == "EUR":
        # If EUR invoice but no tax info -> warn
        if tax is None:
            return ComplianceResult(status="warn", details={"reason": "missing_tax_for_eur"})
        return ComplianceResult(status="pass", details={"rule": "eu_basic"})

    if currency == "SAR":
        # Placeholder for ZATCA checks later
        return ComplianceResult(status="warn", details={"rule": "zATCA_placeholder"})

    return ComplianceResult(status="pass", details={"rule": "default"})

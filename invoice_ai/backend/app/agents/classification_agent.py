from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ClassificationResult:
    invoice_type: str
    language: str
    details: dict


def classify(text_hint: str | None, filename: str) -> ClassificationResult:
    name = (filename or "").lower()
    text = (text_hint or "").lower()

    # Very basic heuristics (rule-based for now)
    if "utility" in name or "electric" in text or "water" in text:
        invoice_type = "utility"
    elif "service" in name or "consult" in text:
        invoice_type = "services"
    elif "invoice" in name or "inv" in name:
        invoice_type = "unknown"
    else:
        invoice_type = "unknown"

    # Language heuristic (super simple)
    if any(w in text for w in ["rechnung", "ust", "mwst"]):
        language = "de"
    elif any(w in text for w in ["فاتورة", "ضريبة"]):
        language = "ar"
    elif text.strip():
        language = "en"
    else:
        language = "unknown"

    return ClassificationResult(
        invoice_type=invoice_type,
        language=language,
        details={"source": "rule_based", "text_hint_used": bool(text_hint)},
    )

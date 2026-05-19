import json
import os
from typing import Any, Dict, Optional, Tuple

GERMAN_ALIAS_TO_INTERNAL = {
    "Hausbesitzer": "solar_owner",
    "Hausbesitzer?": "solar_owner",
    "Eigentümer": "solar_owner",
    "Eigentümer?": "solar_owner",
    "Sind Sie Hauseigentümer?": "solar_owner",
    "Sind Sie Eigentümer?": "solar_owner",
    "Wohneigentum": "solar_owner",
}


def _load_customer_schema() -> Dict[str, Dict[str, Any]]:
    """Load attribute schema from customer_attribute_mapping.json."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "customer_attribute_mapping.json")
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


SCHEMA = _load_customer_schema()


def _get_first(d: Dict[str, Any], keys) -> Any:
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return None


def _as_str(x: Any) -> Optional[str]:
    if x is None:
        return None
    if isinstance(x, (dict, list)):
        return None
    s = str(x).strip()
    return s or None


def _is_numeric_string(value: Any) -> bool:
    # customer considers numeric attributes invalid if non-numeric :contentReference[oaicite:4]{index=4}
    if isinstance(value, (int, float)):
        return True
    s = _as_str(value)
    if s is None:
        return False
    try:
        float(s.replace(",", "."))
        return True
    except ValueError:
        return False


def _validate_attribute(key: str, value: Any) -> Tuple[bool, Optional[Any]]:
    """
    Validate attribute according to customer schema.
    If invalid, return (False, None) so we can drop ONLY the attribute. :contentReference[oaicite:5]{index=5}
    """
    rule = SCHEMA.get(key)
    if not rule:
        return False, None  # unknown attributes: drop

    attr_type = rule.get("attribute_type")
    is_numeric = bool(rule.get("is_numeric"))
    allowed_values = rule.get("values")

    # The API rejects "single-value attribute but array passed" :contentReference[oaicite:6]{index=6}
    if isinstance(value, list):
        return False, None

    # Numeric validation
    if is_numeric:
        if not _is_numeric_string(value):
            return False, None
        # Keep as string to match examples (they send numbers as strings)
        return True, str(value)

    # Dropdown validation
    if attr_type == "dropdown":
        v = _as_str(value)
        if v is None:
            return False, None
        if isinstance(allowed_values, list) and allowed_values:
            if v not in allowed_values:
                return False, None
        return True, v

    # Range validation (schema marks solar_area as "range" + numeric)
    if attr_type == "range":
        if not _is_numeric_string(value):
            return False, None
        return True, str(value)

    # Text (non-numeric)
    v = _as_str(value)
    if v is None:
        return False, None
    return True, v


def process_incoming(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize incoming data into a simpler internal structure:
    { lead: {...}, product: {...}, lead_attributes: {...}, meta_attributes: {...} }
    Incoming lead shape can vary.
    """

    if not isinstance(payload, dict):
        payload = {}

    # Many systems send either top-level fields or nested under "lead"
    lead_in = payload.get("lead") if isinstance(payload.get("lead"), dict) else payload
    product_in = payload.get("product") if isinstance(payload.get("product"), dict) else {}

    # --- Attribute extraction: support "questions" and common variants ---
    attrs_in = None

    # 1) This trigger payload uses "questions"
    if isinstance(payload.get("questions"), dict):
        attrs_in = payload["questions"]

    # 2) common keys (top-level)
    elif isinstance(payload.get("lead_attributes"), dict):
        attrs_in = payload["lead_attributes"]
    elif isinstance(payload.get("attributes"), dict):
        attrs_in = payload["attributes"]
    elif isinstance(payload.get("leadAttributes"), dict):
        attrs_in = payload["leadAttributes"]

    # 3) nested under lead object
    elif isinstance(lead_in, dict) and isinstance(lead_in.get("questions"), dict):
        attrs_in = lead_in["questions"]
    elif isinstance(lead_in, dict) and isinstance(lead_in.get("lead_attributes"), dict):
        attrs_in = lead_in["lead_attributes"]
    elif isinstance(lead_in, dict) and isinstance(lead_in.get("attributes"), dict):
        attrs_in = lead_in["attributes"]
    elif isinstance(lead_in, dict) and isinstance(lead_in.get("leadAttributes"), dict):
        attrs_in = lead_in["leadAttributes"]

    if not isinstance(attrs_in, dict):
        attrs_in = {}

    # --- Map German owner questions to internal key "solar_owner" ---
    OWNER_QUESTION_KEYS = {
        "Sind Sie Eigentümer der Immobilie?",
        "Sind Sie der Eigentümer der Immobilie?",
        "Sind Sie Eigentümer der Immobilie",      # sometimes without "?"
        "Sind Sie der Eigentümer der Immobilie",  # sometimes without "?"
    }

    for k in OWNER_QUESTION_KEYS:
        if k in attrs_in:
            attrs_in["solar_owner"] = attrs_in.get(k)
            break

    # Normalize some common boolean-ish values to "Ja"/"Nein"
    so = attrs_in.get("solar_owner")
    if isinstance(so, bool):
        attrs_in["solar_owner"] = "Ja" if so else "Nein"
    elif isinstance(so, str):
        v = so.strip().lower()
        if v in {"true", "yes", "y", "1"}:
            attrs_in["solar_owner"] = "Ja"
        elif v in {"false", "no", "n", "0"}:
            attrs_in["solar_owner"] = "Nein"

    # --- Meta extraction (optional) ---
    meta_in = payload.get("meta_attributes") if isinstance(payload.get("meta_attributes"), dict) else payload.get("meta", {})
    if not isinstance(meta_in, dict):
        meta_in = {}

    lead = {
        "phone": _get_first(lead_in, ["phone", "telephone", "tel", "mobile"]),
        "email": _get_first(lead_in, ["email"]),
        "first_name": _get_first(lead_in, ["first_name", "firstname", "firstName"]),
        "last_name": _get_first(lead_in, ["last_name", "lastname", "lastName"]),
        "street": _get_first(lead_in, ["street"]),
        "housenumber": _get_first(lead_in, ["housenumber", "house_number", "houseNumber"]),
        "postcode": _get_first(lead_in, ["postcode", "zip", "zipcode", "postal_code", "postalCode"]),
        "city": _get_first(lead_in, ["city"]),
        "country": _get_first(lead_in, ["country"]),
    }

    product = {
        "name": _get_first(product_in, ["name", "product_name", "productName"]) or "solar"
    }

    return {
        "lead": lead,
        "product": product,
        "lead_attributes": attrs_in,
        "meta_attributes": meta_in,
    }



def should_accept(normalized: Dict[str, Any]) -> Tuple[bool, str]:
    lead = normalized["lead"]
    attrs = normalized["lead_attributes"]

    postcode = _as_str(lead.get("postcode")) or ""
    if not postcode.startswith("66"):
        return False, "rejected: postcode not in 66*** region"

    owner = _as_str(attrs.get("solar_owner"))
    if owner != "Ja":
        return False, "rejected: not house owner (solar_owner != Ja)"

    phone = _as_str(lead.get("phone"))
    if not phone:
        # customer requires telephone number :contentReference[oaicite:8]{index=8}
        return False, "rejected: missing phone"

    return True, "accepted"


def build_customer_payload(normalized: Dict[str, Any]) -> Dict[str, Any]:
    """Build payload for customer API. Invalid attributes are removed (not the lead). :contentReference[oaicite:9]{index=9}"""
    lead = normalized["lead"]
    product = normalized["product"]
    attrs_in = normalized["lead_attributes"]
    meta = normalized["meta_attributes"]

    cleaned_attrs: Dict[str, Any] = {}
    for k, v in attrs_in.items():
        ok, cleaned = _validate_attribute(k, v)
        if ok:
            cleaned_attrs[k] = cleaned

    return {
        "lead": {k: v for k, v in lead.items() if v not in (None, "", [])},
        "product": product,
        "lead_attributes": cleaned_attrs,
        "meta_attributes": meta,
    }

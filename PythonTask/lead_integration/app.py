import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from mapper import process_incoming, should_accept, build_customer_payload

load_dotenv()

USER_ID = os.getenv("USER_ID", "").strip()
API_TOKEN = os.getenv("API_TOKEN", "").strip()
CUSTOMER_API = os.getenv("CUSTOMER_API", "").strip()

app = Flask(__name__)

def _auth_headers():
    return {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}


@app.post("/webhook")
def webhook():
    incoming = request.get_json(silent=True) or {}
    
    import json

    
    
    normalized = process_incoming(incoming)
    
    lead = normalized.get("lead", {})
    attrs = normalized.get("lead_attributes", {})
    print(f"[debug] postcode={lead.get('postcode')} solar_owner={attrs.get('solar_owner')} attrs_keys_sample={list(attrs.keys())[:8]}")

    print(f"[debug] postcode={lead.get('postcode')} solar_owner={attrs.get('solar_owner')}")


    ok, reason = should_accept(normalized)
    print(f"[decision] {reason}")

    if not ok:
        return jsonify({"status": "ignored", "reason": reason}), 200

    payload = build_customer_payload(normalized)

    # Send to fake customer API endpoint 
    resp = requests.post(CUSTOMER_API, json=payload, headers=_auth_headers(), timeout=20)
    print(f"[forward] customer_status={resp.status_code}")

    return jsonify({
        "status": "forwarded",
        "customer_status_code": resp.status_code,
        "customer_response": _safe_text(resp.text),
        "sent_payload_preview": payload,
    }), 200



def _safe_text(text: str, limit: int = 800):
    if text is None:
        return None
    text = str(text)
    return text[:limit] + ("..." if len(text) > limit else "")


@app.get("/health")
def health():
    return jsonify({"ok": True, "user_id": USER_ID}), 200


if __name__ == "__main__":
    # Local run
    app.run(host="0.0.0.0", port=5000, debug=True)

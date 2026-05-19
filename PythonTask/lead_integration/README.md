# Lead Integration – CHECKFOX Developer Test Task

This project implements a lightweight webhook service that receives lead/contact data, validates it against customer requirements, normalizes and maps attributes, and forwards accepted leads to a fake customer API.

---

## Goal (Task Summary)

The service fulfills the following requirements:

- Expose a single webhook endpoint (`/webhook`) to receive leads
- Accept **only** leads that meet all conditions:
  - German postcode in the `66***` region
  - The person is the house owner (`solar_owner == "Ja"`)
- Normalize incoming lead payloads with varying structures
- Transform attributes using the provided customer mapping
- Forward accepted leads to the customer API with Bearer authentication
- Provide a health endpoint for quick verification

---

## Tech Stack

- Python 3
- Flask – webhook receiver
- requests – forwarding to customer API
- python-dotenv – environment-based configuration
- Cloudflare Tunnel – public webhook URL for testing

---

## Project Structure

- `app.py` – Flask application with `/webhook` and `/health`
- `mapper.py` – normalization, validation, and mapping logic
- `customer_attribute_mapping.json` – customer attribute mapping (provided)
- `.env` – environment configuration
- `requirements.txt` – Python dependencies
- `README.md` – setup and usage instructions

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt



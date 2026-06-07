import requests
from config import API_URL


def load_sessions(username=None):
    if not username:
        return []

    response = requests.get(f"{API_URL}sessions/{username}")

    if response.status_code == 200:
        return response.json()

    return []


def create_new_session(username=None):
    if not username:
        return None

    response = requests.post(
        f"{API_URL}sessions/create/",
        json={"username": username}
    )

    if response.status_code == 200:
        data = response.json()

        if data.get("success"):
            return data.get("session_id")

    return None


def add_message_to_session(session_id, role, content, sources=None):
    if not session_id:
        return False

    response = requests.post(
        f"{API_URL}sessions/message/",
        json={
            "session_id": session_id,
            "role": role,
            "content": content,
            "sources": sources or []
        }
    )

    return response.status_code == 200


def clear_all_sessions(username=None):
    # We will implement delete/clear sessions later
    return True
import requests
from config import API_URL
from utils.api import get_auth_headers
from config import API_URL
import requests


def load_sessions():
    response = requests.get(
        f"{API_URL}sessions/",
        headers=get_auth_headers()
    )

    if response.status_code == 200:
        return response.json()

    return []


def create_new_session():
    

    response = requests.post(
        f"{API_URL}sessions/create/",
        headers=get_auth_headers()
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



def clear_all_sessions():
    response = requests.delete(
        f"{API_URL}sessions/clear/",
        headers=get_auth_headers()
    )

    return response.status_code == 200
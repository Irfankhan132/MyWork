import json
import uuid
from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path("chat_sessions.json")


def load_sessions():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_sessions(sessions):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=4, ensure_ascii=False)


def create_new_session():
    sessions = load_sessions()

    new_session = {
        "id": str(uuid.uuid4()),
        "title": "New Chat",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": []
    }

    sessions.append(new_session)
    save_sessions(sessions)

    return new_session["id"]


def get_session(session_id):
    sessions = load_sessions()

    for session in sessions:
        if session["id"] == session_id:
            return session

    return None


def generate_chat_title(question):
    words = question.strip().replace("?", "").split()

    if len(words) <= 5:
        return question.strip().replace("?", "").title()

    return " ".join(words[:5]).title()



def add_message_to_session(session_id, role, content, sources=None):
    sessions = load_sessions()

    for session in sessions:
        if session["id"] == session_id:
            session["messages"].append({
                "role": role,
                "content": content,
                "sources": sources or [],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            if session["title"] == "New Chat" and role == "user":
                session["title"] = generate_chat_title(content)

            break

    save_sessions(sessions)


def clear_all_sessions():
    save_sessions([])
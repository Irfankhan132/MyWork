import json
import bcrypt
from pathlib import Path

USERS_FILE = Path("users.json")

def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

def register_user(username, password):
    users = load_users()

    if username in users:
        return False, "User already exists."

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    users[username] = {
        "password": hashed_password
    }

    save_users(users)
    return True, "Registration successful."

def login_user(username, password):
    users = load_users()

    if username not in users:
        return False, "User not found."

    stored_password = users[username]["password"]

    if bcrypt.checkpw(password.encode(), stored_password.encode()):
        return True, "Login successful."

    return False, "Incorrect password."
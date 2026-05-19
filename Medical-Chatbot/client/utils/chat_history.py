import json
from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path("chat_history.json")

def load_chat_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_chat_message(question, answer, sources=None):
    history = load_chat_history()

    history.append({
        "question": question,
        "answer": answer,
        "sources": sources or [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def clear_chat_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=4)
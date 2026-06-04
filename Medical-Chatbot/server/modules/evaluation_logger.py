import json
from pathlib import Path
from datetime import datetime

EVAL_FILE = Path("evaluation_logs.json")


def load_logs():
    if EVAL_FILE.exists():
        with open(EVAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_evaluation_log(username, question, response_time, sources, retrieved_chunks):
    logs = load_logs()

    logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": username,
        "question": question,
        "response_time_seconds": round(response_time, 2),
        "retrieved_chunks": retrieved_chunks,
        "sources": sources
    })

    with open(EVAL_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)


def get_evaluation_logs():
    return load_logs()
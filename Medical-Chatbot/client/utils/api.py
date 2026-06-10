import requests
from config import API_URL
import streamlit as st

def get_auth_headers():
    token = st.session_state.get("token", "")

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}"
    }

def upload_pdfs_api(files):
    files_payload = []

    for f in files:
        f.seek(0)
        file_bytes = f.getvalue()

        files_payload.append(
            ("files", (f.name, file_bytes, "application/pdf"))
        )

    return requests.post(
        f"{API_URL}upload_pdfs/",
        files=files_payload,
        headers=get_auth_headers()
    )

def ask_question(question, chat_history=""):
    return requests.post(
        f"{API_URL}ask/",
        data={
            "question": question,
            "chat_history": chat_history,
    
        },
        headers=get_auth_headers()
    )
    


def get_documents():
    return requests.get(
        f"{API_URL}documents/",
        headers=get_auth_headers()
    )

def delete_document(filename):
    return requests.delete(
        f"{API_URL}documents/{filename}",
        headers=get_auth_headers()
    )


def summarize_document(filename):
    return requests.post(
        f"{API_URL}summary/",
        data={
            "filename": filename
        },
        headers=get_auth_headers()
    )
    
def get_evaluation_data():
    return requests.get(
        f"{API_URL}evaluation/",
        headers=get_auth_headers()
    )
    
    
def register_user_api(username, password):
    return requests.post(
        f"{API_URL}register/",
        json={
            "username": username,
            "password": password
        }
    )


def login_user_api(username, password):
    return requests.post(
        f"{API_URL}login/",
        json={
            "username": username,
            "password": password
        }
    )
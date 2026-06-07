import requests
from config import API_URL

def upload_pdfs_api(files, username):
    files_payload = [("files", (f.name, f.read(), "application/pdf")) for f in files]
    data = {"username": username}
    return requests.post(f"{API_URL}upload_pdfs/", files=files_payload, data=data)

def ask_question(question, chat_history="", username=""):
    return requests.post(
        f"{API_URL}ask/",
        data={
            "question": question,
            "chat_history": chat_history,
            "username": username
        }
    )
    


def get_documents(username):
    return requests.get(f"{API_URL}documents/", params={"username": username})

def delete_document(filename, username):
    return requests.delete(f"{API_URL}documents/{filename}", params={"username": username})


def summarize_document(username, filename):
    return requests.post(
        f"{API_URL}summary/",
        data={
            "username": username,
            "filename": filename
        }
    )
    
def get_evaluation_data(username):
    return requests.get(
        f"{API_URL}evaluation/",
        params={"username": username}
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
import requests
from config import API_URL

def upload_pdfs_api(files):
    files_payload = [("files", (f.name, f.read(), "application/pdf")) for f in files]
    return requests.post(f"{API_URL}upload_pdfs/", files=files_payload)

def ask_question(question, chat_history=""):
    return requests.post(
        f"{API_URL}ask/", 
        data={
            "question": question, 
            "chat_history": chat_history
            }
        )

def get_documents():
    return requests.get(f"{API_URL}documents/")

def delete_document(filename):
    return requests.delete(f"{API_URL}documents/{filename}")
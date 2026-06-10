from fileinput import filename
import json
import streamlit as st
from utils.api import delete_document
from components.upload import render_upload
from components.ChatUI import render_chat
from components.history_download import render_history_download
from utils.api import get_documents
# from utils.auth import login_user, register_user
from utils.api import login_user_api, register_user_api
from utils.chat_history import (
    load_sessions,
    create_new_session,
    clear_all_sessions
)

from utils.api import get_evaluation_data


st.set_page_config(
    page_title="🩺 AI Medical Assistant",
    page_icon="🏥",
    layout="wide"
)

# =========================
# Authentication
# =========================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.authenticated:
    st.title("🩺 AI Medical Assistant")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            response = login_user_api(login_username, login_password)
            data = response.json()

            if data.get("success"):
                st.session_state.authenticated = True
                st.session_state.username = data.get("username")
                st.session_state.token = data.get("access_token")
                st.success(data.get("message"))
                st.rerun()
                
            else:
                st.error(data.get("message"))
                
            

    with tab2:
        st.subheader("Register")
        reg_username = st.text_input("Choose Username", key="reg_username")
        reg_password = st.text_input("Choose Password", type="password", key="reg_password")

        if st.button("Register"):
            response = register_user_api(reg_username, reg_password)
            data = response.json()

            if data.get("success"):
                st.success(data.get("message"))
            else:
                st.error(data.get("message"))

    st.stop()

# =========================
# Session setup
# =========================

if "token" not in st.session_state:
    st.session_state.token = ""
    
    
# st.sidebar.write("Token saved:", bool(st.session_state.token))
# st.sidebar.write("Token preview:", st.session_state.token[:20] + "...")
    
sessions = load_sessions()

if "current_session_id" not in st.session_state:
    if sessions:
        st.session_state.current_session_id = sessions[-1]["id"]
    else:
        st.session_state.current_session_id = create_new_session()



# =========================
# Sidebar
# =========================
st.sidebar.title("🩺 Medical Assistant")
st.sidebar.caption(f"Logged in as: {st.session_state.username}")

if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.token = ""
    st.session_state.messages = []
    st.session_state.current_session_id = None
    st.rerun()

if st.sidebar.button("📊 Evaluation Dashboard"):
    st.session_state.show_evaluation = True

st.sidebar.markdown("---")
st.sidebar.markdown("## 📄 Uploaded Documents")

try:
    response = get_documents()

    if response.status_code == 200:
        documents = response.json().get("documents", [])

        if documents:
            for doc in documents:
                col1, col2 = st.sidebar.columns([4, 1])

                with col1:
                    st.markdown(f"📘 {doc}")

                with col2:
                    if st.button("🗑", key=f"delete_{doc}"):
                        
                        delete_document(doc)
                        st.session_state.pop("document_summary", None)
                        st.session_state.pop("summary_filename", None)
                        st.session_state.pop("suggested_questions", None)
                        st.rerun()
        else:
            st.sidebar.info("No documents uploaded yet.")
    else:
        st.sidebar.error("Could not load documents.")

except Exception:
    st.sidebar.error("Backend server is not running.")

st.sidebar.markdown("---")
st.sidebar.markdown("## ⚙️ Options")

if st.sidebar.button("🧹 Clear Saved History"):
    clear_all_sessions()
    st.session_state.messages = []
    st.session_state.current_session_id = None
    st.rerun()

if st.sidebar.button("➕ New Chat"):
    st.session_state.current_session_id = None
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("## 🕘 Chat History")

sessions = load_sessions()

if sessions:
    for i, session in enumerate(reversed(sessions[-10:])):
        title = session.get("title", "New Chat")

        if st.sidebar.button(f"💬 {title[:35]}...", key=f"session_{i}"):
            st.session_state.current_session_id = session["id"]
            st.session_state.messages = session["messages"]
            st.rerun()

    st.sidebar.download_button(
        label="⬇️ Export History JSON",
        data=json.dumps(sessions, indent=4, ensure_ascii=False),
        file_name="chat_sessions.json",
        mime="application/json"
    )
else:
    st.sidebar.info("No chat history yet.")

# =========================
# Main Page
# =========================
st.title("🩺 Medical Assistant :Chatbot:")


if st.session_state.get("show_evaluation", False):
    st.markdown("## 📊 Evaluation Dashboard")

    response = get_evaluation_data()

    if response.status_code == 200:
        data = response.json()

        col1, col2 = st.columns(2)

        col1.metric("Total Queries", data.get("total_queries", 0))
        col2.metric("Average Response Time", f"{data.get('average_response_time', 0)} sec")

        st.markdown("### Query Logs")

        for log in reversed(data.get("logs", [])[-10:]):
            with st.expander(f"{log['timestamp']} | {log['username']} | {log['question']}"):
                st.write(f"Response Time: {log['response_time_seconds']} sec")
                st.write(f"Retrieved Chunks: {log['retrieved_chunks']}")
                st.write("Sources:")
                st.json(log["sources"])
    else:
        st.error("Could not load evaluation data.")

render_upload()
render_chat()
render_history_download()
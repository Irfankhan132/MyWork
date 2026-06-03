import json
import streamlit as st
from components.upload import render_upload
from components.ChatUI import render_chat
from components.history_download import render_history_download
from utils.api import get_documents
from utils.auth import login_user, register_user
from utils.chat_history import (
    load_sessions,
    create_new_session,
    clear_all_sessions
)

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
            success, message = login_user(login_username, login_password)

            if success:
                st.session_state.authenticated = True
                st.session_state.username = login_username
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with tab2:
        st.subheader("Register")
        reg_username = st.text_input("Choose Username", key="reg_username")
        reg_password = st.text_input("Choose Password", type="password", key="reg_password")

        if st.button("Register"):
            success, message = register_user(reg_username, reg_password)

            if success:
                st.success(message)
            else:
                st.error(message)

    st.stop()

# =========================
# Session setup
# =========================
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
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("## 📄 Uploaded Documents")

try:
    response = get_documents(st.session_state.username)

    if response.status_code == 200:
        documents = response.json().get("documents", [])

        if documents:
            for doc in documents:
                col1, col2 = st.sidebar.columns([4, 1])

                with col1:
                    st.markdown(f"📘 {doc}")

                with col2:
                    if st.button("🗑", key=f"delete_{doc}"):
                        from utils.api import delete_document
                        delete_document(doc, st.session_state.username)
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
    st.rerun()

if st.sidebar.button("➕ New Chat"):
    new_session_id = create_new_session()
    st.session_state.current_session_id = new_session_id
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

render_upload()
render_chat()
render_history_download()
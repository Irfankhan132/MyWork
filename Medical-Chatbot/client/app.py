import json
import streamlit as st
from components.upload import render_upload
from components.ChatUI import render_chat
from components.history_download import render_history_download
from utils.api import get_documents

from utils.chat_history import create_new_session

from utils.chat_history import (
    load_sessions,
    create_new_session,
    get_session,
    clear_all_sessions
)

st.set_page_config(
    page_title="🩺 AI Medical Assistant",
    page_icon="🏥",
    layout="wide"
)

sessions = load_sessions()

if "current_session_id" not in st.session_state:
    if sessions:
        st.session_state.current_session_id = sessions[-1]["id"]
    else:
        st.session_state.current_session_id = create_new_session()

st.sidebar.title("🩺 Medical Assistant")

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
                        from utils.api import delete_document
                        delete_document(doc)
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

st.title("🩺 Medical Assistant :Chatbot:")

render_upload()
render_chat()
render_history_download()
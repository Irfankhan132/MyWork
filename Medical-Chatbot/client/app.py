import streamlit as st
from components.upload import render_upload
from components.ChatUI import render_chat
from components.history_download import render_history_download
from utils.api import get_documents

st.set_page_config(
    page_title="AI Medical Assistant",
    page_icon="🏥",
    layout="wide"
)

st.sidebar.title("🩺 Medical Assistant")

st.sidebar.markdown("## 📄 Uploaded Documents")

try:
    response = get_documents()

    if response.status_code == 200:
        documents = response.json().get("documents", [])

        if documents:
            for doc in documents:
                st.sidebar.markdown(f"📘 {doc}")
        else:
            st.sidebar.info("No documents uploaded yet.")
    else:
        st.sidebar.error("Could not load documents.")

except Exception:
    st.sidebar.error("Backend server is not running.")

st.sidebar.markdown("---")

st.sidebar.markdown("## ⚙️ Options")

if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.rerun()

st.title("Medical Assistant :Chatbot:")

render_upload()
render_chat()
render_history_download()
import json
import streamlit as st
from components.upload import render_upload
from components.ChatUI import render_chat
from components.history_download import render_history_download
from utils.api import get_documents
from utils.chat_history import load_chat_history, clear_chat_history

st.set_page_config(
    page_title="🩺 AI Medical Assistant",
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
    clear_chat_history()
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("## 🕘 Chat History")

history = load_chat_history()

if history:
    for i, item in enumerate(reversed(history[-10:])):
        question = item.get("question", "Untitled question")
        answer = item.get("answer", "")
        sources = item.get("sources", [])

        if st.sidebar.button(f"💬 {question[:35]}...", key=f"history_{i}"):
            st.session_state.messages = [
                {"role": "user", "content": question},
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                }
            ]
            st.rerun()

    st.sidebar.download_button(
        label="⬇️ Export History JSON",
        data=json.dumps(history, indent=4, ensure_ascii=False),
        file_name="chat_history.json",
        mime="application/json"
    )
else:
    st.sidebar.info("No chat history yet.")

st.title("🩺 Medical Assistant :Chatbot:")

render_upload()
render_chat()
render_history_download()
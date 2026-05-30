import streamlit as st
from utils.api import ask_question
from utils.chat_history import add_message_to_session
from pathlib import Path
import time


def show_sources(sources):
    if sources:
        st.markdown("### 📄 Sources")

        displayed = set()

        for src in sources:
            source_path = src.get("source", "")
            page = src.get("page", "")

            file_name = Path(source_path).name
            citation_text = f"{file_name} - Page {page}"

            if citation_text not in displayed:
                pdf_url = f"http://127.0.0.1:8000/uploaded_docs/{file_name}#page={page}"

                st.markdown(f"- [{citation_text}]({pdf_url})")
                displayed.add(citation_text)


def render_chat():
    st.subheader("💬 Ask a question about your medical documents:")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).markdown(msg["content"])

        if msg["role"] == "assistant":
            show_sources(msg.get("sources", []))

    user_input = st.chat_input("Type your question here...")

    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        with st.spinner("Thinking..."):
            chat_history_text = ""
            for msg in st.session_state.messages[-6:]:
                role = msg["role"]
                content = msg["content"]
                chat_history_text += f"{role}: {content}\n"
            response = ask_question(user_input, chat_history_text)

        if response.status_code == 200:
            data = response.json()
            answer = data["response"]
            sources = data.get("sources", [])

            with st.chat_message("assistant"):
                placeholder = st.empty()
                streamed_text = ""

                for word in answer.split():
                    streamed_text += word + " "
                    placeholder.markdown(streamed_text)
                    time.sleep(0.03)

            show_sources(sources)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })

            session_id = st.session_state.current_session_id

            add_message_to_session(session_id, "user", user_input)
            add_message_to_session(session_id, "assistant", answer, sources)

        else:
            st.error("Error getting response from server.")
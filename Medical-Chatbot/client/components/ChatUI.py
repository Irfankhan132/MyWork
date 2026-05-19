import streamlit as st
from utils.api import ask_question
from utils.chat_history import save_chat_message
from pathlib import Path


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
                st.markdown(f"- [{citation_text}](#)")
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

        response = ask_question(user_input)

        if response.status_code == 200:
            data = response.json()
            answer = data["response"]
            sources = data.get("sources", [])

            st.chat_message("assistant").markdown(answer)
            show_sources(sources)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })

            save_chat_message(user_input, answer, sources)

        else:
            st.error("Error getting response from server.")
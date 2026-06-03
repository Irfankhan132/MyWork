import streamlit as st
from utils.api import upload_pdfs_api, get_documents, summarize_document

def render_upload():
    st.sidebar.header("📤 Upload Medical Documents (.PDFs)")
    uploaded_files = st.sidebar.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True
    )

    username = st.session_state.get("username", "guest")

    if st.sidebar.button("Upload DB") and uploaded_files:
        response = upload_pdfs_api(uploaded_files, username)

        if response.status_code == 200:
            st.sidebar.success("Files uploaded successfully!")
            st.rerun()
        else:
            st.sidebar.error(f"Error uploading files to server: {response.text}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🧾 Document Summary")

    try:
        docs_response = get_documents(username)

        if docs_response.status_code == 200:
            documents = docs_response.json().get("documents", [])

            if documents:
                selected_doc = st.sidebar.selectbox(
                    "Select document",
                    documents
                )

                if st.sidebar.button("Generate Summary"):
                    with st.spinner("Generating document summary..."):
                        summary_response = summarize_document(username, selected_doc)

                    if summary_response.status_code == 200:

                        data = summary_response.json()

                        st.session_state.document_summary = data.get(
                            "summary",
                            ""
                        )

                        st.session_state.summary_filename = selected_doc

                        st.session_state.suggested_questions = (
                            data.get(
                                "suggested_questions",
                                ""
                            ).split("\n")
                        )
                        summary = summary_response.json().get("summary", "")
                        st.session_state.document_summary = summary
                        st.session_state.summary_filename = selected_doc
                    else:
                        st.sidebar.error("Error generating summary.")
            else:
                st.sidebar.info("Upload a document to generate summary.")

    except Exception:
        st.sidebar.error("Could not load documents for summary.")

    if "document_summary" in st.session_state:
        
        st.markdown(f"## 🧾 Summary: {st.session_state.summary_filename}")
        st.markdown(st.session_state.document_summary)
        
        if "suggested_questions" in st.session_state:

            st.markdown("## 💡 Suggested Questions")

            for q in st.session_state.suggested_questions:

                q = q.strip()

                if q:
                    if st.button(q, key=f"suggested_{q}"):
                        st.session_state.auto_question = q
                        st.rerun()
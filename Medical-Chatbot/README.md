# 🩺 Medical Assistant Chatbot

An AI-powered Medical Assistant Chatbot built using **FastAPI**, **Streamlit**, **LangChain**, **Pinecone**, and **Groq LLM**.  
This project allows users to upload medical PDF documents and ask questions based on the uploaded content using Retrieval-Augmented Generation (RAG).

---

# 🚀 Features

- Upload medical PDF books/documents
- Extract and process text from PDFs
- Split documents into semantic chunks
- Generate embeddings using HuggingFace embeddings
- Store embeddings in Pinecone Vector Database
- Ask questions related to uploaded documents
- AI-generated responses using Groq LLM
- Streamlit chatbot interface
- FastAPI backend APIs

---

# 🛠️ Tech Stack

## Backend
- Python
- FastAPI
- LangChain
- Pinecone
- HuggingFace Embeddings
- Groq API

## Frontend
- Streamlit

## Vector Database
- Pinecone

---

# 📁 Project Structure

```text
Medical-Chatbot/
│
├── client/
│   ├── components/
│   ├── utils/
│   ├── app.py
│   └── requirements.txt
│
├── server/
│   ├── middlewares/
│   ├── modules/
│   ├── routers/
│   ├── uploaded_docs/
│   ├── main.py
│   └── requirements.txt
│
├── .gitignore
└── README.md


## ⚠️ Disclaimer

This project is for educational and research purposes only.

It should not be considered a replacement for professional medical advice, diagnosis, or treatment.
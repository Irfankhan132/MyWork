# 🩺 AI Medical Assistant

An AI-powered Medical Document Assistant built with **FastAPI**, **Streamlit**, **LangChain**, **Pinecone**, **HuggingFace Embeddings**, **Groq LLMs**, **PostgreSQL**, and **JWT Authentication**.

The application allows users to upload medical PDF documents or any pdf docs and interact with them using natural language. It uses Retrieval-Augmented Generation (RAG), semantic search, hybrid retrieval, reranking, and source-grounded responses to answer questions based on uploaded medical documents.

---

## 🚀 Key Features

### 📄 Medical Document Management

* Upload one or multiple PDF documents
* Store documents separately for each authenticated user
* Automatic PDF parsing, chunking, and embedding
* View uploaded documents in the sidebar
* Delete uploaded documents and related Pinecone vectors
* Prevent duplicate vectors when the same document is re-uploaded

### 🤖 RAG-Based Medical Question Answering

* Ask questions about uploaded medical PDFs
* Retrieval-Augmented Generation using Pinecone and LangChain
* Context-aware answers using previous chat history
* Source-grounded answers with PDF name and page number
* Clickable citations that open the referenced PDF page
* User-specific retrieval using JWT-based authentication

### 🔎 Hybrid Search and Reranking

* Dense semantic search using HuggingFace embeddings
* Keyword-based scoring for exact medical terms
* Hybrid ranking using vector score and keyword score
* Top candidate chunks are reranked before being sent to the LLM
* Improves retrieval quality for medical terminology and follow-up questions

### 🧠 Conversation Memory

* Maintains context across follow-up questions
* Understands references such as:

  * "it"
  * "its symptoms"
  * "this disease"
  * "that condition"
* Supports natural multi-turn medical document conversations

### 💬 Multi-Chat Sessions

* Create multiple independent chat sessions
* Switch between previous conversations
* Smart chat title generation
* Chat messages stored in PostgreSQL
* Clear user-specific chat history

### 🧾 AI Document Summary

* Generate structured summaries for uploaded PDFs
* Extract:

  * Short summary
  * Key medical topics
  * Symptoms mentioned
  * Treatments or medications mentioned
  * Important notes

### 💡 Suggested Questions

* Generate useful questions based on the selected document
* Helps users explore uploaded PDFs more easily
* Suggested questions can be clicked and used directly in the chat

### 🔐 Authentication and Security

* User registration and login
* Password hashing using bcrypt
* JWT token generation after login
* Protected FastAPI routes using JWT
* User-specific documents, chats, summaries, and evaluation logs
* API keys and secrets stored in environment variables

### 📊 Evaluation Dashboard

* User-specific evaluation dashboard
* Tracks:

  * Total queries
  * Average response time
  * Retrieved chunks
  * Sources used
  * Query logs
* Evaluation logs stored in PostgreSQL

---

## 🏗️ System Architecture

```text
┌─────────────────────────────┐
│       Streamlit Client      │
│   Login, Upload, Chat UI    │
└──────────────┬──────────────┘
               │ JWT Token
               ▼
┌─────────────────────────────┐
│        FastAPI Backend      │
│ Auth, Upload, RAG, Summary  │
└───────┬───────────┬─────────┘
        │           │
        ▼           ▼
┌──────────────┐  ┌────────────────┐
│ PostgreSQL   │  │  Pinecone DB   │
│ Users, Chats │  │ Vector Search  │
│ Logs         │  │ User Vectors   │
└──────────────┘  └───────┬────────┘
                          │
                          ▼
┌─────────────────────────────┐
│   HuggingFace Embeddings    │
│ sentence-transformers       │
│ all-MiniLM-L6-v2            │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│   Hybrid Retrieval Layer    │
│ Vector Search + Keywords    │
│ Reranking                   │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│      LangChain Pipeline     │
│ Context Construction        │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│          Groq LLM           │
│ Medical Response Generation │
└─────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Frontend

* Streamlit
* Requests

### Backend

* FastAPI
* Uvicorn
* SQLAlchemy

### Database

* PostgreSQL

### Authentication

* bcrypt
* JWT
* python-jose

### AI / LLM

* LangChain
* Groq API
* Llama / Qwen models

### Vector Database

* Pinecone

### Embeddings

* HuggingFace
* sentence-transformers/all-MiniLM-L6-v2

### PDF Processing

* PyPDF
* LangChain PDF loaders

### Utilities

* Python Dotenv
* Loguru
* TQDM

---

## 📂 Project Structure

```text
Medical-Chatbot/
│
├── client/
│   ├── app.py
│   ├── components/
│   │   ├── ChatUI.py
│   │   ├── upload.py
│   │   └── history_download.py
│   ├── utils/
│   │   ├── api.py
│   │   └── chat_history.py
│   └── requirements.txt
│
├── server/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── security.py
│   ├── create_tables.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── upload_pdfs.py
│   │   ├── ask_question.py
│   │   ├── documents.py
│   │   ├── summary.py
│   │   ├── evaluation.py
│   │   └── chat_sessions.py
│   ├── modules/
│   │   ├── load_vectorstore.py
│   │   ├── llm.py
│   │   ├── query_handlers.py
│   │   └── evaluation_logger.py
│   ├── uploaded_docs/
│   ├── requirements.txt
│   └── .env
│
├── screenshots/
├── README.md
└── .gitignore
```

---

## 🔄 Application Workflow

### 1. User Authentication

The user registers or logs in through the Streamlit interface. Passwords are hashed using bcrypt and stored in PostgreSQL. After login, the backend returns a JWT token.

### 2. JWT-Protected API Requests

The frontend sends the JWT token with protected API requests. The backend extracts the username from the token and uses it for user-specific operations.

### 3. PDF Upload

The user uploads medical PDF files. Files are stored in a user-specific folder:

```text
server/uploaded_docs/<username>/
```

### 4. Document Processing

Uploaded PDFs are parsed, split into chunks, and converted into embeddings using HuggingFace embeddings.

### 5. Vector Storage

Embeddings are stored in Pinecone with metadata such as:

```text
source
page
text
user_id
```

### 6. User Question

The user asks a question. The backend retrieves relevant chunks only from that user’s documents.

### 7. Hybrid Retrieval and Reranking

The system combines semantic vector search with keyword scoring and reranks retrieved chunks before sending the best context to the LLM.

### 8. LLM Response

Groq LLM generates an answer using the retrieved context and conversation history.

### 9. Source Citation

The response includes source PDF names and page numbers. Citations are clickable and open the referenced PDF page.

### 10. Evaluation Logging

Each query is logged with response time, retrieved chunks, sources, and username in PostgreSQL.

---

## 🔐 Security Features

* Password hashing using bcrypt
* JWT-based login system
* Protected FastAPI endpoints
* User-specific document isolation
* User-specific chat sessions
* User-specific evaluation dashboard
* Environment variables for API keys and database credentials
* No hardcoded secrets

---

## 📊 Evaluation Dashboard

The application includes a user-specific evaluation dashboard that tracks:

* Total queries
* Average response time
* Question history
* Retrieved chunks
* Source documents used
* Hybrid retrieval scores

This helps monitor the performance and reliability of the RAG system.

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/Irfankhan132/MyWork.git
cd MyWork/Medical-Chatbot
```

---

## 2. Backend Setup

```bash
cd server
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Create a `.env` file inside the `server/` folder:

```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_pinecone_index_name

DATABASE_URL=postgresql://postgres:your_password@localhost:5432/medical_chatbot

JWT_SECRET_KEY=your_super_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Run the backend:

```bash
python -m uvicorn main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

---

## 3. PostgreSQL Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE medical_chatbot;
```

Create tables using SQLAlchemy:

```bash
cd server
python create_tables.py
```

Expected tables:

```text
users
chat_sessions
chat_messages
evaluation_logs
```

---

## 4. Frontend Setup

Open a second terminal:

```bash
cd client
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Frontend runs on:

```text
http://localhost:8501
```

---

## ✅ Completed Phases

### Phase 1 — RAG Foundation

* FastAPI backend
* Streamlit frontend
* PDF upload
* Pinecone vector database
* HuggingFace embeddings
* Groq LLM integration
* RAG-based question answering
* Source citations
* Multi-chat sessions
* Conversation memory
* Chat history export

### Phase 2 — Product-Level Features

* User-specific document isolation
* PDF citation preview
* AI document summary
* Suggested questions
* Document deletion
* Duplicate vector prevention

### Phase 3 — Resume-Level AI Engineering

* Hybrid search
* Reranking
* Evaluation dashboard
* Query logging
* Response time tracking
* Source tracking

### Phase 4 — Production Architecture

* PostgreSQL database integration
* SQLAlchemy ORM
* JWT authentication
* Secure API route protection
* PostgreSQL-backed users
* PostgreSQL-backed chat sessions
* PostgreSQL-backed evaluation logs

---

## 🚀 Planned Improvements

* Cookie-based login persistence
* Docker and Docker Compose support
* Cloud deployment
* Admin analytics dashboard
* Feedback system for answers
* Role-based access control
* More advanced reranking models
* BM25-based hybrid search
* Medical report summarization modes
* Voice-based queries
* Knowledge Graph / GraphRAG integration with Neo4j

---

## 👨‍💻 Author

**Irfan Ullah Khan**

MSc Computer Engineering (University of Padua, Italy)
BSc Software Engineering (Comsats University Islamabad, Pakistan)

Interests:

* Retrieval-Augmented Generation
* Knowledge Graphs
* Generative AI
* Machine Learning
* Data Engineering
* Software Development
* Java Development
* Database Engineering

GitHub:
https://github.com/Irfankhan132/MyWork

LinkedIn:
https://www.linkedin.com/in/irfan-khan-developer/

---

## ⭐ Support

If you find this project useful, consider giving it a star on GitHub.

Feedback, suggestions, and contributions are welcome.

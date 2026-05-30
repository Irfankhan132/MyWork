# 🩺 AI Medical Assistant

An AI-powered Medical Document Assistant built using **FastAPI**, **Streamlit**, **LangChain**, **Pinecone**, **HuggingFace Embeddings**, and **Groq LLMs**.

The application allows users to upload medical PDF documents and interact with them using natural language. By combining Retrieval-Augmented Generation (RAG) with semantic search, the assistant provides grounded answers based on uploaded documents while maintaining conversation context across multiple chat sessions.

---

## 🚀 Features

### 📄 Medical Document Management

* Upload one or multiple PDF documents
* Automatic document processing and chunking
* Semantic indexing using vector embeddings
* View uploaded documents
* Delete uploaded documents

### 🤖 AI-Powered Question Answering

* Ask questions about uploaded medical documents
* Retrieval-Augmented Generation (RAG)
* Context-aware responses
* Source-grounded answers
* Citation tracking with page references
* Groq-powered LLM integration

### 🧠 Conversation Memory

* Maintains context across follow-up questions
* Supports natural conversations
* Understands references such as:

  * "it"
  * "its symptoms"
  * "this disease"
  * "that condition"

### 💬 Multi-Chat Sessions

* Create multiple chat sessions
* Switch between conversations
* Persistent session storage
* Smart chat title generation
* Chat history management

### 🔐 User Authentication

* User registration
* Secure login system
* Password hashing using bcrypt
* Local user storage

### 📚 Chat History

* Persistent chat storage
* Reload previous conversations
* Export chat history as JSON
* Clear saved chat history

### ⚡ User Experience

* Streaming response effect
* Loading indicators
* Source references
* Clean and responsive interface

---

# 🏗️ System Architecture

```text
┌─────────────────────────┐
│     Streamlit Client    │
│      Frontend UI        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│        FastAPI          │
│      Backend API        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ PDF Processing Module   │
│ Parsing & Chunking      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ HuggingFace Embeddings  │
│ all-MiniLM-L6-v2        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      Pinecone DB        │
│    Vector Storage       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      LangChain          │
│ Retrieval Pipeline      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│       Groq LLM          │
│      Qwen3-32B          │
└─────────────────────────┘
```

---

# 🛠️ Technology Stack

## Frontend

* Streamlit

## Backend

* FastAPI
* Uvicorn

## LLM & AI

* LangChain
* Groq API
* Qwen3-32B

## Vector Database

* Pinecone

## Embeddings

* HuggingFace
* all-MiniLM-L6-v2

## Authentication

* bcrypt

## PDF Processing

* PyPDF

## Utilities

* Python Dotenv
* Requests
* Loguru
* TQDM

---

# 📂 Project Structure

```text
Medical-Chatbot/
│
├── client/
│   ├── app.py
│   ├── components/
│   ├── utils/
│   ├── users.json
│   └── chat_sessions.json
│
├── server/
│   ├── main.py
│   ├── routers/
│   ├── modules/
│   ├── uploads/
│   ├── requirements.txt
│   └── .env
│
├── screenshots/
│
├── README.md
│
└── .gitignore
```

---

# 🔄 How It Works

### Step 1

User uploads medical PDF documents.

### Step 2

Documents are parsed and split into chunks.

### Step 3

Chunks are converted into embeddings using:

```text
all-MiniLM-L6-v2
```

### Step 4

Embeddings are stored inside Pinecone.

### Step 5

User asks a question.

### Step 6

Relevant chunks are retrieved from Pinecone.

### Step 7

LangChain constructs the prompt using retrieved context.

### Step 8

Groq LLM generates an answer.

### Step 9

Answer and document citations are returned to the user.

---

# 🔒 Security Features

* Password hashing using bcrypt
* Environment variables for API keys
* No hardcoded credentials
* User authentication system
* Session-based access control

---

# 📸 Screenshots (Coming Soon)

### Login Page

Add screenshot here:

```text
screenshots/login.png
```

### Registration Page

```text
screenshots/register.png
```

### PDF Upload

```text
screenshots/upload.png
```

### Chat Interface

```text
screenshots/chat.png
```

### Source Citations

```text
screenshots/sources.png
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/your-username/AI-Medical-Assistant.git
cd AI-Medical-Assistant
```

---

## Backend Setup

```bash
cd server

python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt
```

Create `.env`

```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_index_name
```

Run Backend

```bash
python -m uvicorn main:app --reload
```

Backend runs on:

```text
http://localhost:8000
```

---

## Frontend Setup

```bash
cd client

pip install streamlit requests bcrypt
```

Run Frontend

```bash
streamlit run app.py
```

Frontend runs on:

```text
http://localhost:8501
```

---

# 🎯 Current Status (Part 1)

### Completed

✅ User Authentication

✅ PDF Upload & Processing

✅ Pinecone Vector Search

✅ HuggingFace Embeddings

✅ Groq LLM Integration

✅ RAG Pipeline

✅ Conversation Memory

✅ Multi-Chat Sessions

✅ Smart Chat Titles

✅ Chat History Export

✅ Source Citations

✅ Streaming Responses

✅ Document Management

---

# 🚀 Planned Features (Part 2)

* PDF Preview on Citation Click
* User-Specific Document Isolation
* Cloud Deployment
* Admin Dashboard
* JWT Authentication
* Docker Support
* CI/CD Pipeline
* Role-Based Access Control
* Medical Report Summarization
* Voice-Based Queries
* Advanced Search Filters

---

# 👨‍💻 Author

**Irfan Ullah Khan**

MSc Computer Engineering

Specialization:

* Knowledge Graphs
* Retrieval-Augmented Generation (RAG)
* Generative AI
* Machine Learning
* Data Engineering
* Software Development

GitHub:
https://github.com/Irfankhan132/MyWork

LinkedIn:
https://www.linkedin.com/in/irfan-khan-developer/

---

## ⭐ Support

If you find this project useful, consider giving it a star on GitHub.

Feedback, suggestions, and contributions are always welcome.

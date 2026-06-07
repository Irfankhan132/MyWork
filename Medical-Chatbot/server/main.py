from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.exception_handlers import catch_exception_middleware
from routers.upload_pdfs import router as upload_router
from routers.ask_question import router as ask_router
from routers.documents import router as documents_router
from fastapi.staticfiles import StaticFiles
from routers.summary import router as summary_router
from routers.evaluation import router as evaluation_router
from routers.auth import router as auth_router
from routers.chat_sessions import router as chat_router

# app = FastAPI(
#     title="Medical Assistant API", description="API for AI Medical Assistant Chatbot"
# )

app = FastAPI(title="Medical Assistant API")

app.mount("/uploaded_docs", StaticFiles(directory="uploaded_docs"), name="uploaded_docs")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# middleware exception handlers
app.middleware("http")(catch_exception_middleware)

# routers

# 1. upload pdf doc
app.include_router(upload_router)

# 2. another router for asking query
app.include_router(ask_router)

app.include_router(documents_router)
app.include_router(summary_router)
app.include_router(evaluation_router)
app.include_router(auth_router)
app.include_router(chat_router)
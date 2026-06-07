from fastapi import APIRouter
from pydantic import BaseModel
from database import SessionLocal
from models import User, ChatSession, ChatMessage
from datetime import datetime
import uuid
import json

router = APIRouter()


class SessionCreate(BaseModel):
    username: str


class MessageCreate(BaseModel):
    session_id: str
    role: str
    content: str
    sources: list = []


@router.post("/sessions/create/")
def create_session(data: SessionCreate):

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.username == data.username)
            .first()
        )

        if not user:
            return {"success": False}

        session = ChatSession(
            session_id=str(uuid.uuid4()),
            title="New Chat",
            user_id=user.id
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return {
            "success": True,
            "session_id": session.session_id
        }

    finally:
        db.close()
        
        
@router.get("/sessions/{username}")
def get_sessions(username: str):

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if not user:
            return []

        sessions = (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user.id)
            .order_by(ChatSession.created_at.desc())
            .all()
        )

        results = []

        for session in sessions:

            messages = []

            for msg in session.messages:
                messages.append({
                    "role": msg.role,
                    "content": msg.content,
                    "sources": json.loads(msg.sources)
                    if msg.sources else []
                })

            results.append({
                "id": session.session_id,
                "title": session.title,
                "messages": messages
            })

        return results

    finally:
        db.close()
        
        
@router.post("/sessions/message/")
def add_message(data: MessageCreate):

    db = SessionLocal()

    try:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.session_id == data.session_id)
            .first()
        )

        if not session:
            return {"success": False}

        message = ChatMessage(
            role=data.role,
            content=data.content,
            sources=json.dumps(data.sources),
            session_id=session.id
        )

        db.add(message)

        if (
            session.title == "New Chat"
            and data.role == "user"
        ):
            session.title = data.content[:40]

        db.commit()

        return {"success": True}

    finally:
        db.close()
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
import bcrypt

router = APIRouter()


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/register/")
def register(user: UserRegister):

    db: Session = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.username == user.username)
            .first()
        )

        if existing_user:
            return {
                "success": False,
                "message": "User already exists."
            }

        hashed_password = (
            bcrypt.hashpw(
                user.password.encode(),
                bcrypt.gensalt()
            )
            .decode()
        )

        new_user = User(
            username=user.username,
            password=hashed_password
        )

        db.add(new_user)
        db.commit()

        return {
            "success": True,
            "message": "Registration successful."
        }

    finally:
        db.close()


@router.post("/login/")
def login(user: UserLogin):

    db: Session = SessionLocal()

    try:
        db_user = (
            db.query(User)
            .filter(User.username == user.username)
            .first()
        )

        if not db_user:
            return {
                "success": False,
                "message": "User not found."
            }

        if bcrypt.checkpw(
            user.password.encode(),
            db_user.password.encode()
        ):
            return {
                "success": True,
                "message": "Login successful."
            }

        return {
            "success": False,
            "message": "Incorrect password."
        }

    finally:
        db.close()
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
import bcrypt
from security import create_access_token

router = APIRouter()


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/register/")
def register(db_user: UserRegister):

    db: Session = SessionLocal()

    try:
        existing_user = (
            db.query(User)
            .filter(User.username == db_user.username)
            .first()
        )

        if existing_user:
            return {
                "success": False,
                "message": "User already exists."
            }

        hashed_password = (
            bcrypt.hashpw(
                db_user.password.encode(),
                bcrypt.gensalt()
            )
            .decode()
        )

        new_user = User(
            username=db_user.username,
            password=hashed_password
        )

        db.add(new_user)
        db.commit()

        access_token = create_access_token(
            data={"sub": db_user.username}
        )
        
        return {
            "success": True,
            "message": "Registration successful.",
            "access_token": access_token,
            "token_type": "bearer",
            "username": db_user.username
        }

    finally:
        db.close()


@router.post("/login/")
def login(user_input: UserLogin):

    db: Session = SessionLocal()

    try:
        db_user = (
            db.query(User)
            .filter(User.username == user_input.username)
            .first()
        )

        if not db_user:
            return {
                "success": False,
                "message": "User not found."
            }

        if bcrypt.checkpw(
            user_input.password.encode(),
            db_user.password.encode()
        ):
            access_token = create_access_token(
                data={"sub": db_user.username}
            )

            return {
                "success": True,
                "message": "Login successful.",
                "access_token": access_token,
                "token_type": "bearer",
                "username": db_user.username
            }

        return {
            "success": False,
            "message": "Incorrect password."
        }

    finally:
        db.close()
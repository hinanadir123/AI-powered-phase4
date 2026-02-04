from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timedelta
import jwt
from models import User
from db import get_session
from dependencies import SECRET_KEY

router = APIRouter(prefix="/auth", tags=["auth"])

# Request models for auth endpoints
class UserLogin(BaseModel):
    email: str
    password: str  # In a real app, passwords would be hashed

class UserRegister(BaseModel):
    name: str
    email: str
    password: str  # In a real app, passwords would be hashed

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=User)
def register_user(user_data: UserRegister, session: Session = Depends(get_session)):
    try:
        print(f"Attempting to register user: {user_data.email}")

        # Check if user already exists
        existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
        if existing_user:
            print(f"User already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        # Create new user
        user_id = str(uuid.uuid4())
        new_user = User(
            id=user_id,
            email=user_data.email,
            name=user_data.name
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        print(f"Successfully registered user: {new_user.email}")
        return new_user
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
def login_user(user_data: UserLogin, session: Session = Depends(get_session)):
    try:
        print(f"Attempting to login user: {user_data.email}")

        # Find user by email
        user = session.exec(select(User).where(User.email == user_data.email)).first()

        if not user:
            print(f"User not found: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        print(f"User found: {user.email}, ID: {user.id}")

        # In a real app, we would verify the password hash here
        # For this demo, we'll skip password verification

        # Create JWT token
        token_data = {
            "userId": user.id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
        }

        token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")

        print(f"Successfully logged in user: {user.email}")
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        print(f"Login HTTP error for user")
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )
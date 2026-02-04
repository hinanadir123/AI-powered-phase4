from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional
from datetime import timedelta
from ..core.config import settings
from ..core.security import create_access_token, verify_password, get_password_hash
from ..models.user import User
from ..core.database import get_session
from pydantic import BaseModel


router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login", response_model=Token)
def login(request: LoginRequest, session: Session = Depends(get_session)):
    """Login endpoint to authenticate user and return JWT token."""
    # Query for user by email
    statement = select(User).where(User.email == request.email)
    user = session.exec(statement).first()

    # Note: In a real implementation, you would have a password field in the User model
    # For now, we'll skip password verification for demo purposes
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=Token)
def register(request: LoginRequest, session: Session = Depends(get_session)):
    """Register a new user and return JWT token."""
    # Check if user already exists
    statement = select(User).where(User.email == request.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    # Create new user
    user = User(
        email=request.email,
        name=request.email.split("@")[0],  # Use email prefix as name
        auth_provider="better-auth",
        auth_provider_user_id=""  # Will be set by Better Auth
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
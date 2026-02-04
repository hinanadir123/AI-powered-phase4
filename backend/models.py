from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class UserBase(SQLModel):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, nullable=False)
    name: Optional[str] = Field(default=None)


class User(UserBase, table=True):
    __tablename__ = "users"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    __tablename__ = "tasks"
    
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Indexes will be handled by the database
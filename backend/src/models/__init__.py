from uuid import uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .task import Task
    from .message import Message


class User(SQLModel, table=True):
    """
    Represents an authenticated user with unique identifier, 
    authentication tokens, and associations to their tasks and conversations.
    """
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(unique=True, nullable=False)
    name: str = Field(max_length=100, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    auth_provider: str = Field(nullable=False)
    auth_provider_user_id: str = Field(nullable=False)

    # Relationships
    tasks: list["Task"] = Relationship(back_populates="user")
    conversations: list["Conversation"] = Relationship(back_populates="user")
    messages: list["Message"] = Relationship(back_populates="user")


class Conversation(SQLModel, table=True):
    """
    Represents a session of interaction between a user and the AI assistant, 
    containing metadata like start/end times and associated user.
    """
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    user_id: str = Field(foreign_key="user.id", nullable=False)

    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: list["Message"] = Relationship(back_populates="conversation")
    tasks: list["Task"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """
    Represents an individual exchange within a conversation, 
    including sender (user/AI), timestamp, and content.
    """
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    content: str = Field(nullable=False)
    sender_type: str = Field(sa_column_kwargs={"check": "sender_type IN ('user', 'ai')"}, nullable=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    conversation_id: str = Field(foreign_key="conversation.id", nullable=False)
    user_id: str = Field(foreign_key="user.id", nullable=False)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    user: User = Relationship(back_populates="messages")


class Task(SQLModel, table=True):
    """
    Represents a user's to-do item with properties like title, 
    description, status, and timestamps.
    """
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: str = Field(min_length=1, max_length=200, nullable=False)
    description: Optional[str] = Field(max_length=1000, default=None)
    status: str = Field(default="pending", sa_column_kwargs={"check": "status IN ('pending', 'completed')"})
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)
    user_id: str = Field(foreign_key="user.id", nullable=False)
    conversation_id: Optional[str] = Field(foreign_key="conversation.id", default=None)

    # Relationships
    user: User = Relationship(back_populates="tasks")
    conversation: Optional[Conversation] = Relationship(back_populates="tasks")
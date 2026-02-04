from uuid import uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from .task import Task
    from .conversation import Conversation
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
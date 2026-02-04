from uuid import uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from .user import User
    from .message import Message
    from .task import Task


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
from uuid import uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from .user import User
    from .conversation import Conversation


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
    conversation: "Conversation" = Relationship(back_populates="messages")
    user: User = Relationship(back_populates="messages")
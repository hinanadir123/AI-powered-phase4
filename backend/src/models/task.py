from uuid import uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from .user import User
    from .conversation import Conversation


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
    conversation: Optional["Conversation"] = Relationship(back_populates="tasks")
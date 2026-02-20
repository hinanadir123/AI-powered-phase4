"""
Task: T5.2.1, T5.2.2 - Add Priorities and Tags to Task Model
Spec Reference: phase5-spec.md Section 3.1.1, 3.1.2
Constitution: constitution.md v5.0

This module defines the updated Task model with priority enum and tags relationship.
"""

from uuid import uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional, List
from enum import Enum


if TYPE_CHECKING:
    from backend.src.models.user import User
    from backend.src.models.conversation import Conversation


class PriorityLevel(str, Enum):
    """Priority levels for tasks as per phase5-spec.md Section 3.1.1"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Tag(SQLModel, table=True):
    """
    Tag model for categorizing tasks.
    Implements many-to-many relationship with Task model.
    Task: T5.2.2 - phase5-spec.md Section 3.1.2
    """
    __tablename__ = "tags"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(max_length=50, nullable=False, unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    tasks: List["TaskTag"] = Relationship(back_populates="tag")


class TaskTag(SQLModel, table=True):
    """
    Association table for many-to-many relationship between Task and Tag.
    Task: T5.2.2 - phase5-spec.md Section 3.1.2
    """
    __tablename__ = "task_tags"

    task_id: str = Field(foreign_key="task.id", primary_key=True)
    tag_id: str = Field(foreign_key="tags.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    task: "Task" = Relationship(back_populates="task_tags")
    tag: Tag = Relationship(back_populates="tasks")


class Task(SQLModel, table=True):
    """
    Enhanced Task model with priority and tags support.
    Tasks: T5.2.1, T5.2.2
    Spec: phase5-spec.md Sections 3.1.1, 3.1.2
    """
    __tablename__ = "task"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: str = Field(min_length=1, max_length=200, nullable=False)
    description: Optional[str] = Field(max_length=1000, default=None)
    status: str = Field(default="pending", sa_column_kwargs={"check": "status IN ('pending', 'completed')"})

    # T5.2.1: Priority field (enum: low, medium, high, urgent)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM, nullable=False, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    completed_at: Optional[datetime] = Field(default=None)
    user_id: str = Field(foreign_key="user.id", nullable=False, index=True)
    conversation_id: Optional[str] = Field(foreign_key="conversation.id", default=None)

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    conversation: Optional["Conversation"] = Relationship(back_populates="tasks")

    # T5.2.2: Many-to-many relationship with tags
    task_tags: List[TaskTag] = Relationship(back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    @property
    def tags(self) -> List[str]:
        """Return list of tag names for this task"""
        return [task_tag.tag.name for task_tag in self.task_tags]

"""
Task: T5.2.3, T5.2.4, T5.2.5 - Enhanced Task Model with Search, Filter, Sort Support
Spec Reference: phase5-spec.md Sections 3.1.3, 3.1.4, 3.1.5
Constitution: constitution.md v5.0

This module defines the Task model with:
- T5.2.3: Full-text search support (title, description)
- T5.2.4: Filter support (status, priority, tags, due_date)
- T5.2.5: Sort support (due_date, priority, created_at, title)
"""

from uuid import uuid4
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship, Column, Index
from sqlalchemy import Text
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
    Enhanced Task model with comprehensive search, filter, and sort support.

    Tasks: T5.2.1, T5.2.2, T5.2.3, T5.2.4, T5.2.5
    Spec: phase5-spec.md Sections 3.1.1-3.1.5

    Features:
    - Priority levels (low, medium, high, urgent)
    - Tags (many-to-many relationship)
    - Due dates for filtering and sorting
    - Full-text search on title and description
    - Indexed fields for performance (<500ms requirement)
    """
    __tablename__ = "task"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    # T5.2.3: Searchable fields (title and description)
    title: str = Field(min_length=1, max_length=200, nullable=False, index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))

    status: str = Field(
        default="pending",
        sa_column_kwargs={"check": "status IN ('pending', 'completed')"},
        index=True
    )

    # T5.2.1: Priority field with index for filtering and sorting
    priority: PriorityLevel = Field(
        default=PriorityLevel.MEDIUM,
        nullable=False,
        index=True
    )

    # T5.2.4: Due date field for filtering and sorting
    due_date: Optional[date] = Field(default=None, index=True)

    # T5.2.5: Timestamps for sorting
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True
    )
    completed_at: Optional[datetime] = Field(default=None)

    user_id: str = Field(foreign_key="user.id", nullable=False, index=True)
    conversation_id: Optional[str] = Field(foreign_key="conversation.id", default=None)

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    conversation: Optional["Conversation"] = Relationship(back_populates="tasks")

    # T5.2.2: Many-to-many relationship with tags
    task_tags: List[TaskTag] = Relationship(
        back_populates="task",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @property
    def tags(self) -> List[str]:
        """Return list of tag names for this task"""
        return [task_tag.tag.name for task_tag in self.task_tags]

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue (has due_date in the past and not completed)"""
        if self.due_date and self.status != "completed":
            return self.due_date < date.today()
        return False


# Create composite indexes for common query patterns
# These improve performance for search, filter, and sort operations
__table_args__ = (
    # Index for filtering by user and status
    Index('idx_task_user_status', 'user_id', 'status'),

    # Index for filtering by user and priority
    Index('idx_task_user_priority', 'user_id', 'priority'),

    # Index for filtering by user and due_date
    Index('idx_task_user_due_date', 'user_id', 'due_date'),

    # Index for sorting by created_at
    Index('idx_task_user_created', 'user_id', 'created_at'),
)

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum


class UserBase(SQLModel):
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, nullable=False)
    name: Optional[str] = Field(default=None)


class User(UserBase, table=True):
    __tablename__ = "users"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PriorityLevel(str, Enum):
    """Priority levels for tasks - Phase 5 feature"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecurrencePattern(str, Enum):
    """Recurrence patterns for tasks - Phase 5 feature"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Tag(SQLModel, table=True):
    """Tag model for categorizing tasks - Phase 5 feature"""
    __tablename__ = "tags"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, nullable=False, unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskTag(SQLModel, table=True):
    """Association table for Task-Tag many-to-many relationship - Phase 5 feature"""
    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
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

    # Phase 5 fields
    priority: str = Field(default="medium", nullable=False, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    reminder_time: Optional[datetime] = Field(default=None, index=True)  # Added index for faster querying
    recurrence_pattern: Optional[str] = Field(default=None, index=True)  # Added index for faster querying
    recurrence_end_date: Optional[datetime] = Field(default=None)
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id", index=True)  # Added index for faster querying

    # Additional fields to support advanced features
    next_occurrence: Optional[datetime] = Field(default=None, index=True)  # For tracking next occurrence of recurring tasks
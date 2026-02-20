# Task: T5.3.1, T5.3.5 - Add Recurring Tasks, Due Dates, and Reminders to Task Model
# Spec Reference: phase5-spec.md Section 3.2 (Advanced Features)
# Constitution: constitution.md v5.0 Section 4.4 (Advanced Features Implementation)
#
# This file contains the updated Task model with:
# - Recurrence object (interval, frequency, days, end_date)
# - Due date field
# - Reminder object (enabled, time_before, channels)
#
# Version: 1.0
# Date: 2026-02-15

from uuid import uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import JSON
from typing import TYPE_CHECKING, Optional, List, Dict, Any
from enum import Enum


if TYPE_CHECKING:
    from .user import User
    from .conversation import Conversation


class PriorityEnum(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RecurrenceIntervalEnum(str, Enum):
    """Recurrence interval types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class TaskAdvanced(SQLModel, table=True):
    """
    Advanced Task model with recurring tasks, due dates, reminders, priorities, and tags.

    Features:
    - Priorities: low, medium, high, urgent
    - Tags: Multiple tags for categorization
    - Recurrence: Automatic task creation on intervals
    - Due dates: Deadline tracking
    - Reminders: Scheduled notifications
    """
    __tablename__ = "tasks"

    # Basic fields
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: str = Field(min_length=1, max_length=200, nullable=False)
    description: Optional[str] = Field(max_length=1000, default=None)
    status: str = Field(default="pending", sa_column_kwargs={"check": "status IN ('pending', 'in-progress', 'completed')"})

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)

    # Intermediate features (T5.2.1, T5.2.2)
    priority: str = Field(default="medium", sa_column_kwargs={"check": "priority IN ('low', 'medium', 'high', 'urgent')"})
    tags: List[str] = Field(default=[], sa_column=Column(JSON))

    # Advanced features (T5.3.1, T5.3.5)
    due_date: Optional[datetime] = Field(default=None)

    # Recurrence object structure:
    # {
    #   "enabled": true,
    #   "interval": "weekly",  // daily, weekly, monthly, custom
    #   "frequency": 1,
    #   "days": ["monday", "wednesday"],  // for weekly
    #   "end_date": "2026-12-31"
    # }
    recurrence: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    # Reminder object structure:
    # {
    #   "enabled": true,
    #   "time_before": "1h",  // 15m, 30m, 1h, 1d, 1w
    #   "channels": ["email", "push"]
    # }
    reminder: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    # Parent task ID for recurring tasks
    parent_task_id: Optional[str] = Field(default=None)

    # Foreign keys
    user_id: str = Field(foreign_key="user.id", nullable=False)
    conversation_id: Optional[str] = Field(foreign_key="conversation.id", default=None)

    # Relationships
    user: "User" = Relationship(back_populates="tasks")
    conversation: Optional["Conversation"] = Relationship(back_populates="tasks")


class RecurrenceConfig(SQLModel):
    """Pydantic model for recurrence configuration validation"""
    enabled: bool = True
    interval: RecurrenceIntervalEnum
    frequency: int = Field(ge=1, le=365, default=1)
    days: Optional[List[str]] = Field(default=None)  # For weekly: ["monday", "wednesday"]
    end_date: Optional[datetime] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "interval": "weekly",
                "frequency": 1,
                "days": ["monday", "wednesday"],
                "end_date": "2026-12-31T00:00:00Z"
            }
        }


class ReminderConfig(SQLModel):
    """Pydantic model for reminder configuration validation"""
    enabled: bool = True
    time_before: str = Field(pattern=r"^\d+[mhdw]$")  # 15m, 30m, 1h, 1d, 1w
    channels: List[str] = Field(default=["email"])

    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "time_before": "1h",
                "channels": ["email", "push"]
            }
        }


class TaskCreate(SQLModel):
    """Schema for creating a new task"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(max_length=1000, default=None)
    priority: str = Field(default="medium")
    tags: List[str] = Field(default=[])
    due_date: Optional[datetime] = Field(default=None)
    recurrence: Optional[Dict[str, Any]] = Field(default=None)
    reminder: Optional[Dict[str, Any]] = Field(default=None)


class TaskUpdate(SQLModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(min_length=1, max_length=200, default=None)
    description: Optional[str] = Field(max_length=1000, default=None)
    status: Optional[str] = Field(default=None)
    priority: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)
    recurrence: Optional[Dict[str, Any]] = Field(default=None)
    reminder: Optional[Dict[str, Any]] = Field(default=None)


class TaskResponse(SQLModel):
    """Schema for task response"""
    id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    tags: List[str]
    due_date: Optional[datetime]
    recurrence: Optional[Dict[str, Any]]
    reminder: Optional[Dict[str, Any]]
    parent_task_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    user_id: str
    conversation_id: Optional[str]

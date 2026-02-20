"""
Advanced Task Models with Recurrence, Due Dates, Reminders
Task: T5.3.1 - Implements advanced Task model with all required fields
Model Reference: Extended from base models.py with additional fields
Specification: phase5-spec.md Section 3.2 (Advanced Features)
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum
import json


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
    CUSTOM = "custom"  # For cron expressions


class ReminderChannel(str, Enum):
    """Channels for sending reminders"""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"


class RecurrenceInfo(SQLModel):
    """
    Model to represent recurrence configuration structure
    This structure will be stored as JSON in the recurrence_pattern field
    """
    enabled: bool = Field(default=False)
    interval: str = Field(default="daily")  # daily, weekly, monthly, yearly, custom
    frequency: int = Field(default=1)  # repeat every n interval units
    days: List[str] = Field(default_factory=list)  # for weekly patterns: ["monday", "wednesday"]
    day: int = Field(default=1)  # for monthly patterns: day of month (1-31)
    month: int = Field(default=1)  # for yearly patterns: month (1-12)
    cron_expression: Optional[str] = Field(default=None)  # for custom cron expressions
    end_date: Optional[datetime] = Field(default=None)  # when to stop recurrence
    max_occurrences: Optional[int] = Field(default=None)  # maximum number of occurrences


class ReminderInfo(SQLModel):
    """
    Model to represent reminder configuration
    """
    enabled: bool = Field(default=False)
    time_before: str = Field(default="1h")  # 1h, 30m, 1d, etc.
    channels: List[ReminderChannel] = Field(default_factory=list)
    last_sent: Optional[datetime] = Field(default=None)


class TaskAdvanced(BaseModel):
    """
    Extended Task model with all advanced features
    """
    id: Optional[int] = None
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    completed: bool = Field(default=False)

    # Advanced fields
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM, nullable=False, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    reminder_time: Optional[datetime] = Field(default=None, index=True)  # Specific time to send reminder

    # New advanced fields with proper defaults and configurations
    recurrence_info: Optional[RecurrenceInfo] = Field(default=None)  # JSON field with recurrence settings
    reminder_info: Optional[ReminderInfo] = Field(default=None)     # JSON field with reminder settings
    next_occurrence: Optional[datetime] = Field(default=None, index=True)  # Next time this task should recur
    original_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")  # For recurring task instances

    # Metadata
    user_id: str = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreateAdvanced(BaseModel):
    """Schema for creating tasks with advanced features"""
    title: str
    description: Optional[str] = None
    priority: Optional[PriorityLevel] = PriorityLevel.MEDIUM
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    recurrence_info: Optional[RecurrenceInfo] = None
    reminder_info: Optional[ReminderInfo] = None
    next_occurrence: Optional[datetime] = None


class TaskUpdateAdvanced(BaseModel):
    """Schema for updating tasks with advanced features"""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[PriorityLevel] = None
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    recurrence_info: Optional[RecurrenceInfo] = None
    reminder_info: Optional[ReminderInfo] = None
    next_occurrence: Optional[datetime] = None


class TaskReadAdvanced(BaseModel):
    """Schema for reading tasks with advanced features"""
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    priority: PriorityLevel
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    recurrence_info: Optional[RecurrenceInfo] = None
    reminder_info: Optional[ReminderInfo] = None
    next_occurrence: Optional[datetime] = None
    original_task_id: Optional[int] = None
    user_id: str
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []
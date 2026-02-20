from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    title: str  # Required field
    priority: Optional[str] = "medium"
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    recurrence_pattern: Optional[str] = None
    recurrence_end_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    recurrence_pattern: Optional[str] = None
    recurrence_end_date: Optional[datetime] = None
    next_occurrence: Optional[datetime] = None


class TaskToggleComplete(BaseModel):
    completed: bool


class TaskRead(TaskBase):
    id: int
    user_id: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    priority: str
    tags: List[str] = []
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    recurrence_pattern: Optional[str] = None
    recurrence_end_date: Optional[datetime] = None
    parent_task_id: Optional[int] = None
    next_occurrence: Optional[datetime] = None


class TaskListQuery(BaseModel):
    status: Optional[str] = "all"  # all, pending, completed
    sort: Optional[str] = "created"  # created, title
    priority: Optional[str] = None
    tags: Optional[str] = None
    search: Optional[str] = None
    due_from: Optional[datetime] = None
    due_to: Optional[datetime] = None
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    title: str  # Required field


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskToggleComplete(BaseModel):
    completed: bool


class TaskRead(TaskBase):
    id: int
    user_id: str
    completed: bool
    created_at: datetime
    updated_at: datetime


class TaskListQuery(BaseModel):
    status: Optional[str] = "all"  # all, pending, completed
    sort: Optional[str] = "created"  # created, title
"""
Task: T5.2.1, T5.2.2 - Pydantic Schemas for Priorities and Tags
Spec Reference: phase5-spec.md Section 3.1.1, 3.1.2
Constitution: constitution.md v5.0

This module defines request/response schemas for priority and tag features.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class PriorityLevel(str, Enum):
    """Priority levels enum - T5.2.1"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TagBase(BaseModel):
    """Base schema for tags - T5.2.2"""
    name: str = Field(min_length=1, max_length=50)


class TagCreate(TagBase):
    """Schema for creating a new tag - T5.2.2"""
    pass


class TagRead(TagBase):
    """Schema for reading tag data - T5.2.2"""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class TaskCreate(TaskBase):
    """
    Schema for creating a task with priority and tags.
    Tasks: T5.2.1, T5.2.2
    """
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    tags: List[str] = Field(default_factory=list, description="List of tag names")


class TaskUpdate(BaseModel):
    """
    Schema for updating a task.
    Tasks: T5.2.1, T5.2.2
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[PriorityLevel] = None
    tags: Optional[List[str]] = None


class TaskRead(TaskBase):
    """
    Schema for reading task data with priority and tags.
    Tasks: T5.2.1, T5.2.2
    """
    id: str
    user_id: str
    status: str
    priority: PriorityLevel
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskListQuery(BaseModel):
    """
    Query parameters for listing tasks with filtering and sorting.
    Tasks: T5.2.1, T5.2.2
    Spec: phase5-spec.md Sections 3.1.1, 3.1.2, 3.1.5
    """
    status: Optional[str] = Field(default="all", description="Filter by status: all, pending, completed")
    priority: Optional[PriorityLevel] = Field(default=None, description="Filter by priority: low, medium, high, urgent")
    tags: Optional[str] = Field(default=None, description="Filter by tags (comma-separated): work,urgent")
    sort: Optional[str] = Field(default="created:desc", description="Sort by: created, priority, title (add :asc or :desc)")


class AddTagRequest(BaseModel):
    """Request schema for adding a tag to a task - T5.2.2"""
    tag: str = Field(min_length=1, max_length=50)


class TaskListResponse(BaseModel):
    """Response schema for task list"""
    tasks: List[TaskRead]
    total: int
    filters_applied: dict

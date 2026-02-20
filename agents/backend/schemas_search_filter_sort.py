"""
Task: T5.2.3, T5.2.4, T5.2.5 - Pydantic Schemas for Search, Filter, Sort
Spec Reference: phase5-spec.md Sections 3.1.3, 3.1.4, 3.1.5
Constitution: constitution.md v5.0

This module defines request/response schemas for search, filter, and sort features.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime, date
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
    Schema for creating a task with priority, tags, and due date.
    Tasks: T5.2.1, T5.2.2, T5.2.4
    """
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    tags: List[str] = Field(default_factory=list, description="List of tag names")
    due_date: Optional[date] = Field(default=None, description="Due date for the task")

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tag names"""
        if v:
            # Remove duplicates and empty strings
            v = list(set([tag.strip() for tag in v if tag.strip()]))
            # Validate length
            for tag in v:
                if len(tag) > 50:
                    raise ValueError(f"Tag '{tag}' exceeds maximum length of 50 characters")
        return v


class TaskUpdate(BaseModel):
    """
    Schema for updating a task.
    Tasks: T5.2.1, T5.2.2, T5.2.4
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[PriorityLevel] = None
    tags: Optional[List[str]] = None
    due_date: Optional[date] = None

    @validator('tags')
    def validate_tags(cls, v):
        """Validate tag names"""
        if v is not None:
            # Remove duplicates and empty strings
            v = list(set([tag.strip() for tag in v if tag.strip()]))
            # Validate length
            for tag in v:
                if len(tag) > 50:
                    raise ValueError(f"Tag '{tag}' exceeds maximum length of 50 characters")
        return v


class TaskRead(TaskBase):
    """
    Schema for reading task data with all features.
    Tasks: T5.2.1, T5.2.2, T5.2.3, T5.2.4, T5.2.5
    """
    id: str
    user_id: str
    status: str
    priority: PriorityLevel
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[date] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SearchFilterSortQuery(BaseModel):
    """
    Comprehensive query parameters for search, filter, and sort.
    Tasks: T5.2.3, T5.2.4, T5.2.5
    Spec: phase5-spec.md Sections 3.1.3, 3.1.4, 3.1.5
    """
    # T5.2.3: Search parameter
    search: Optional[str] = Field(
        default=None,
        description="Search keyword for title and description (case-insensitive)"
    )

    # T5.2.4: Filter parameters
    status: Optional[str] = Field(
        default=None,
        description="Filter by status: pending, completed"
    )
    priority: Optional[PriorityLevel] = Field(
        default=None,
        description="Filter by priority: low, medium, high, urgent"
    )
    tags: Optional[str] = Field(
        default=None,
        description="Filter by tags (comma-separated, AND logic): work,urgent"
    )
    due_from: Optional[date] = Field(
        default=None,
        description="Filter tasks due from this date (inclusive)"
    )
    due_to: Optional[date] = Field(
        default=None,
        description="Filter tasks due until this date (inclusive)"
    )

    # T5.2.5: Sort parameter
    sort: Optional[str] = Field(
        default="created_at:desc",
        description="Sort by field:direction (due_date, priority, created_at, title)"
    )

    @validator('status')
    def validate_status(cls, v):
        """Validate status filter"""
        if v and v not in ["pending", "completed"]:
            raise ValueError("Status must be 'pending' or 'completed'")
        return v

    @validator('sort')
    def validate_sort(cls, v):
        """Validate sort parameter"""
        if v:
            parts = v.split(":")
            if len(parts) != 2:
                raise ValueError("Sort must be in format 'field:direction'")

            field, direction = parts
            valid_fields = ["due_date", "priority", "created_at", "title"]
            if field not in valid_fields:
                raise ValueError(f"Sort field must be one of: {', '.join(valid_fields)}")

            if direction not in ["asc", "desc"]:
                raise ValueError("Sort direction must be 'asc' or 'desc'")
        return v

    @validator('due_to')
    def validate_date_range(cls, v, values):
        """Validate that due_to is after due_from"""
        if v and 'due_from' in values and values['due_from']:
            if v < values['due_from']:
                raise ValueError("due_to must be after or equal to due_from")
        return v


class AddTagRequest(BaseModel):
    """Request schema for adding a tag to a task - T5.2.2"""
    tag: str = Field(min_length=1, max_length=50)


class TaskListResponse(BaseModel):
    """
    Response schema for task list with metadata.
    Tasks: T5.2.3, T5.2.4, T5.2.5
    """
    tasks: List[TaskRead]
    total: int
    filters_applied: dict = Field(
        description="Dictionary of filters that were applied to the query"
    )


class SearchStats(BaseModel):
    """
    Statistics for search results - T5.2.3
    Useful for debugging and performance monitoring
    """
    query: str
    results_count: int
    execution_time_ms: float
    filters_applied: dict

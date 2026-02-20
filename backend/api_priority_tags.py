"""
Task: T5.2.1, T5.2.2 - API Endpoints for Priorities and Tags
Spec Reference: phase5-spec.md Section 3.1.1, 3.1.2
Constitution: constitution.md v5.0

This module implements REST API endpoints for task priority and tag management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, col
from typing import List, Optional
from datetime import datetime

from backend.src.core.database import get_session
from backend.src.models.user import User
from backend.src.api.middleware.auth_middleware import get_current_user
from .schemas_priority_tags import (
    TaskCreate, TaskUpdate, TaskRead, TaskListQuery, TaskListResponse,
    AddTagRequest, TagRead, PriorityLevel
)
from .models_priority_tags import Task, Tag, TaskTag


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = Query("all", description="Filter by status: all, pending, completed"),
    priority: Optional[PriorityLevel] = Query(None, description="Filter by priority"),
    tags: Optional[str] = Query(None, description="Comma-separated tag names"),
    sort: Optional[str] = Query("created:desc", description="Sort field:direction"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    List tasks with filtering and sorting support.
    Tasks: T5.2.1, T5.2.2

    Endpoints:
    - GET /tasks?priority=high (T5.2.1)
    - GET /tasks?tags=work,urgent (T5.2.2)
    - GET /tasks?sort=priority:desc (T5.2.1)
    """
    # Build base query
    query = select(Task).where(Task.user_id == current_user.id)

    filters_applied = {}

    # T5.2.1: Filter by priority
    if priority:
        query = query.where(Task.priority == priority)
        filters_applied["priority"] = priority

    # Filter by status
    if status and status != "all":
        if status in ["pending", "completed"]:
            query = query.where(Task.status == status)
            filters_applied["status"] = status

    # T5.2.2: Filter by tags
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            # Join with task_tags and tags tables
            query = (
                query
                .join(TaskTag, Task.id == TaskTag.task_id)
                .join(Tag, TaskTag.tag_id == Tag.id)
                .where(col(Tag.name).in_(tag_list))
            )
            filters_applied["tags"] = tag_list

    # T5.2.1: Sort by priority or other fields
    sort_field, sort_direction = "created", "desc"
    if sort:
        parts = sort.split(":")
        sort_field = parts[0]
        sort_direction = parts[1] if len(parts) > 1 else "desc"

    # Apply sorting
    if sort_field == "priority":
        # Custom priority ordering: urgent > high > medium > low
        priority_order = {"urgent": 1, "high": 2, "medium": 3, "low": 4}
        # Note: This requires a CASE statement in production SQL
        if sort_direction == "desc":
            query = query.order_by(Task.priority.desc())
        else:
            query = query.order_by(Task.priority.asc())
    elif sort_field == "created":
        if sort_direction == "desc":
            query = query.order_by(Task.created_at.desc())
        else:
            query = query.order_by(Task.created_at.asc())
    elif sort_field == "title":
        if sort_direction == "desc":
            query = query.order_by(Task.title.desc())
        else:
            query = query.order_by(Task.title.asc())

    # Execute query
    tasks = session.exec(query).all()

    # Convert to response format
    task_reads = []
    for task in tasks:
        task_read = TaskRead(
            id=task.id,
            title=task.title,
            description=task.description,
            user_id=task.user_id,
            status=task.status,
            priority=task.priority,
            tags=task.tags,
            created_at=task.created_at,
            completed_at=task.completed_at
        )
        task_reads.append(task_read)

    return TaskListResponse(
        tasks=task_reads,
        total=len(task_reads),
        filters_applied=filters_applied
    )


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task with priority and tags.
    Tasks: T5.2.1, T5.2.2
    """
    # Create task
    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        user_id=current_user.id
    )
    session.add(task)
    session.flush()  # Get task ID before adding tags

    # T5.2.2: Add tags
    if task_data.tags:
        for tag_name in task_data.tags:
            # Get or create tag
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.flush()

            # Create task-tag association
            task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
            session.add(task_tag)

    session.commit()
    session.refresh(task)

    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        user_id=task.user_id,
        status=task.status,
        priority=task.priority,
        tags=task.tags,
        created_at=task.created_at,
        completed_at=task.completed_at
    )


@router.post("/{task_id}/tags", response_model=TaskRead)
async def add_tag_to_task(
    task_id: str,
    tag_request: AddTagRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Add a tag to a task.
    Task: T5.2.2
    Endpoint: POST /tasks/{id}/tags
    """
    # Get task
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get or create tag
    tag = session.exec(select(Tag).where(Tag.name == tag_request.tag)).first()
    if not tag:
        tag = Tag(name=tag_request.tag)
        session.add(tag)
        session.flush()

    # Check if association already exists
    existing = session.exec(
        select(TaskTag).where(TaskTag.task_id == task_id, TaskTag.tag_id == tag.id)
    ).first()

    if not existing:
        task_tag = TaskTag(task_id=task_id, tag_id=tag.id)
        session.add(task_tag)
        session.commit()

    session.refresh(task)

    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        user_id=task.user_id,
        status=task.status,
        priority=task.priority,
        tags=task.tags,
        created_at=task.created_at,
        completed_at=task.completed_at
    )


@router.delete("/{task_id}/tags/{tag_name}", response_model=TaskRead)
async def remove_tag_from_task(
    task_id: str,
    tag_name: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a tag from a task.
    Task: T5.2.2
    Endpoint: DELETE /tasks/{id}/tags/{tag}
    """
    # Get task
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get tag
    tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()

    if tag:
        # Remove association
        task_tag = session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id, TaskTag.tag_id == tag.id)
        ).first()

        if task_tag:
            session.delete(task_tag)
            session.commit()

    session.refresh(task)

    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        user_id=task.user_id,
        status=task.status,
        priority=task.priority,
        tags=task.tags,
        created_at=task.created_at,
        completed_at=task.completed_at
    )


@router.get("/tags", response_model=List[TagRead])
async def list_all_tags(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    List all available tags.
    Task: T5.2.2
    """
    tags = session.exec(select(Tag).order_by(Tag.name)).all()
    return tags

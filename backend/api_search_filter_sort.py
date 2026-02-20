"""
Task: T5.2.3, T5.2.4, T5.2.5 - Search, Filter, and Sort API Implementation
Spec Reference: phase5-spec.md Sections 3.1.3, 3.1.4, 3.1.5
Constitution: constitution.md v5.0

This module implements comprehensive search, filter, and sort functionality for tasks.
- T5.2.3: Full-text search using PostgreSQL
- T5.2.4: Multi-criteria filtering (status, priority, tags, due date range)
- T5.2.5: Flexible sorting (due_date, priority, created_at, title)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, col, func, or_, and_
from typing import List, Optional
from datetime import datetime, date

from backend.src.core.database import get_session
from backend.src.models.user import User
from backend.src.api.middleware.auth_middleware import get_current_user
from .schemas_search_filter_sort import (
    TaskCreate, TaskUpdate, TaskRead, TaskListResponse,
    AddTagRequest, TagRead, PriorityLevel, SearchFilterSortQuery
)
from .models_search_filter_sort import Task, Tag, TaskTag


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    # T5.2.3: Search parameter
    search: Optional[str] = Query(None, description="Search in title and description"),

    # T5.2.4: Filter parameters
    status: Optional[str] = Query(None, description="Filter by status: pending, completed"),
    priority: Optional[PriorityLevel] = Query(None, description="Filter by priority"),
    tags: Optional[str] = Query(None, description="Comma-separated tag names"),
    due_from: Optional[date] = Query(None, description="Filter tasks due from this date"),
    due_to: Optional[date] = Query(None, description="Filter tasks due until this date"),

    # T5.2.5: Sort parameter
    sort: Optional[str] = Query("created_at:desc", description="Sort by: due_date, priority, created_at, title (add :asc or :desc)"),

    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    List tasks with comprehensive search, filter, and sort capabilities.

    Tasks: T5.2.3, T5.2.4, T5.2.5

    Examples:
    - GET /tasks?search=meeting
    - GET /tasks?status=pending&priority=high&tags=work&due_from=2026-02-15&due_to=2026-02-20
    - GET /tasks?sort=due_date:asc
    - GET /tasks?search=meeting&priority=high&tags=work&sort=due_date:asc

    Performance: < 500ms as per phase5-spec.md Section 5.6
    """
    # Build base query
    query = select(Task).where(Task.user_id == current_user.id)

    filters_applied = {}

    # T5.2.3: Full-text search on title and description
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                col(Task.title).ilike(search_term),
                col(Task.description).ilike(search_term)
            )
        )
        filters_applied["search"] = search

    # T5.2.4: Filter by status
    if status:
        if status not in ["pending", "completed"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid status. Must be 'pending' or 'completed'"
            )
        query = query.where(Task.status == status)
        filters_applied["status"] = status

    # T5.2.4: Filter by priority
    if priority:
        query = query.where(Task.priority == priority)
        filters_applied["priority"] = priority

    # T5.2.4: Filter by due date range
    if due_from:
        query = query.where(Task.due_date >= due_from)
        filters_applied["due_from"] = due_from.isoformat()

    if due_to:
        query = query.where(Task.due_date <= due_to)
        filters_applied["due_to"] = due_to.isoformat()

    # T5.2.4: Filter by tags (AND logic - all tags must match)
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if tag_list:
            # Join with task_tags and tags tables
            query = (
                query
                .join(TaskTag, Task.id == TaskTag.task_id)
                .join(Tag, TaskTag.tag_id == Tag.id)
                .where(col(Tag.name).in_(tag_list))
                .group_by(Task.id)
                .having(func.count(TaskTag.tag_id) == len(tag_list))
            )
            filters_applied["tags"] = tag_list

    # T5.2.5: Sort by specified field and direction
    sort_field, sort_direction = "created_at", "desc"
    if sort:
        parts = sort.split(":")
        sort_field = parts[0]
        sort_direction = parts[1] if len(parts) > 1 else "desc"

        # Validate sort field
        valid_sort_fields = ["due_date", "priority", "created_at", "title"]
        if sort_field not in valid_sort_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field. Must be one of: {', '.join(valid_sort_fields)}"
            )

        # Validate sort direction
        if sort_direction not in ["asc", "desc"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid sort direction. Must be 'asc' or 'desc'"
            )

    # Apply sorting
    if sort_field == "due_date":
        # Handle NULL due_dates (put them at the end)
        if sort_direction == "desc":
            query = query.order_by(Task.due_date.desc().nullslast())
        else:
            query = query.order_by(Task.due_date.asc().nullslast())
    elif sort_field == "priority":
        # Priority ordering: urgent > high > medium > low
        if sort_direction == "desc":
            query = query.order_by(Task.priority.desc())
        else:
            query = query.order_by(Task.priority.asc())
    elif sort_field == "created_at":
        if sort_direction == "desc":
            query = query.order_by(Task.created_at.desc())
        else:
            query = query.order_by(Task.created_at.asc())
    elif sort_field == "title":
        if sort_direction == "desc":
            query = query.order_by(Task.title.desc())
        else:
            query = query.order_by(Task.title.asc())

    filters_applied["sort"] = f"{sort_field}:{sort_direction}"

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
            due_date=task.due_date,
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
    Create a new task with priority, tags, and due date.
    Tasks: T5.2.1, T5.2.2, T5.2.4
    """
    # Create task
    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        due_date=task_data.due_date,
        user_id=current_user.id
    )
    session.add(task)
    session.flush()  # Get task ID before adding tags

    # Add tags
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
        due_date=task.due_date,
        created_at=task.created_at,
        completed_at=task.completed_at
    )


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update a task including priority, tags, and due date.
    Tasks: T5.2.1, T5.2.2, T5.2.4
    """
    # Get task
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.status = "completed" if task_data.completed else "pending"
        if task_data.completed:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.due_date is not None:
        task.due_date = task_data.due_date

    # Update tags if provided
    if task_data.tags is not None:
        # Remove existing tags
        existing_task_tags = session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id)
        ).all()
        for task_tag in existing_task_tags:
            session.delete(task_tag)

        # Add new tags
        for tag_name in task_data.tags:
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.flush()

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
        due_date=task.due_date,
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
    """
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
        due_date=task.due_date,
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
    """
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
        due_date=task.due_date,
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

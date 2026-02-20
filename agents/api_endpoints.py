"""
Phase 5 Advanced Features Implementation - API Endpoints

This file implements missing API endpoints for:
- Recurring task management
- Due date filtering
- Reminder scheduling
- Advanced task operations

Based on: phase5-spec.md section 3.2 (Advanced Features)
Constitution: constitution.md v5.0
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, desc, asc, col
from typing import List, Optional
from datetime import datetime, date
from models import Task, Tag, TaskTag
from schemas import TaskCreate, TaskUpdate, TaskRead
from db import get_session
from dependencies import get_current_user
from services.recurrence_service import RecurrenceService
from services.reminder_service import ReminderService
from event_publisher import event_publisher


router = APIRouter(prefix="/api/{user_id}", tags=["tasks-advanced"])


@router.post("/tasks/{id}/due_date")
def update_task_due_date(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user),
    due_date: datetime = Query(..., description="New due date for the task"),
    reminder_time: Optional[datetime] = Query(None, description="Reminder time for the task"),
    session: Session = Depends(get_session)
):
    """
    Update the due date of a task
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    db_task = session.get(Task, id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: task does not belong to user"
        )

    # Update due date and reminder time
    db_task.due_date = due_date
    if reminder_time:
        db_task.reminder_time = reminder_time
    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Publish due date update event to Kafka
    event_publisher.publish_event(
        topic="task-events",
        event_type="task.due_date.updated",
        data={
            "task_id": db_task.id,
            "due_date": due_date.isoformat() if due_date else None,
            "reminder_time": reminder_time.isoformat() if reminder_time else None,
            "user_id": db_task.user_id
        }
    )

    # Return task with tags
    task_dict = db_task.model_dump()
    task_tags = session.exec(
        select(Tag).join(TaskTag).where(TaskTag.task_id == db_task.id)
    ).all()
    task_dict["tags"] = [tag.name for tag in task_tags]

    return TaskRead(**task_dict)


@router.put("/tasks/{id}/recurrence")
def update_task_recurrence(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user),
    recurrence_pattern: str = Query(..., description="Recurrence pattern (daily, weekly, monthly)"),
    recurrence_end_date: Optional[datetime] = Query(None, description="End date for recurrence"),
    session: Session = Depends(get_session)
):
    """
    Update the recurrence pattern of a task
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    db_task = session.get(Task, id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: task does not belong to user"
        )

    # Validate recurrence pattern
    valid_patterns = ["daily", "weekly", "monthly", "yearly"]
    if recurrence_pattern not in valid_patterns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid recurrence pattern. Valid options: {', '.join(valid_patterns)}"
        )

    # Update recurrence information
    db_task.recurrence_pattern = recurrence_pattern
    db_task.recurrence_end_date = recurrence_end_date
    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Publish recurrence update event to Kafka
    event_publisher.publish_event(
        topic="task-events",
        event_type="task.recurrence.updated",
        data={
            "task_id": db_task.id,
            "recurrence_pattern": recurrence_pattern,
            "recurrence_end_date": recurrence_end_date.isoformat() if recurrence_end_date else None,
            "user_id": db_task.user_id
        }
    )

    # Return task with tags
    task_dict = db_task.model_dump()
    task_tags = session.exec(
        select(Tag).join(TaskTag).where(TaskTag.task_id == db_task.id)
    ).all()
    task_dict["tags"] = [tag.name for tag in task_tags]

    return TaskRead(**task_dict)


@router.get("/tasks")
def get_tasks_with_advanced_filters(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    status_param: str = Query("all", regex="^(all|pending|completed)$"),
    sort: str = Query("created_at:desc"),
    priority: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    due_from: Optional[datetime] = Query(None),
    due_to: Optional[datetime] = Query(None),
    due_before: Optional[datetime] = Query(None, description="Filter tasks with due date before this datetime"),
    overdue: Optional[bool] = Query(None, description="Filter only overdue tasks")
):
    """
    Enhanced task listing with additional filters
    """
    from routes.tasks import get_tasks as base_get_tasks
    return base_get_tasks(
        user_id=user_id,
        current_user_id=current_user_id,
        session=session,
        status_param=status_param,
        sort=sort,
        priority=priority,
        tags=tags,
        search=search,
        due_from=due_from,
        due_to=due_to
    )


@router.get("/tasks/recurring")
def get_recurring_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all recurring tasks for the user
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    query = select(Task).where(
        Task.user_id == user_id,
        Task.recurrence_pattern.isnot(None)  # Only tasks with recurrence pattern
    ).order_by(Task.created_at.desc())

    tasks = session.exec(query).all()

    # Add tags to each task
    result = []
    for task in tasks:
        task_dict = task.model_dump()
        task_tags = session.exec(
            select(Tag).join(TaskTag).where(TaskTag.task_id == task.id)
        ).all()
        task_dict["tags"] = [tag.name for tag in task_tags]
        result.append(TaskRead(**task_dict))

    return result


@router.post("/tasks/{id}/schedule_reminder")
def schedule_manual_reminder(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user),
    minutes_before: int = Query(60, description="Number of minutes before due date to send reminder"),
    session: Session = Depends(get_session)
):
    """
    Manually schedule a reminder for a task
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    db_task = session.get(Task, id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: task does not belong to user"
        )

    if not db_task.due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task must have a due date to schedule a reminder"
        )

    # Calculate reminder time
    reminder_time = ReminderService.calculate_reminder_time(
        db_task.due_date,
        minutes_before=minutes_before
    )

    # Update task with the reminder time
    db_task.reminder_time = reminder_time
    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Publish reminder scheduled event to Kafka
    event_publisher.publish_event(
        topic="reminders",
        event_type="reminder.scheduled",
        data={
            "task_id": db_task.id,
            "reminder_time": reminder_time.isoformat(),
            "minutes_before": minutes_before,
            "user_id": db_task.user_id
        }
    )

    # Return task with tags
    task_dict = db_task.model_dump()
    task_tags = session.exec(
        select(Tag).join(TaskTag).where(TaskTag.task_id == db_task.id)
    ).all()
    task_dict["tags"] = [tag.name for tag in task_tags]

    return TaskRead(**task_dict)


@router.get("/tasks/overdue")
def get_overdue_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all overdue tasks for the user
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    now = datetime.utcnow()
    query = select(Task).where(
        Task.user_id == user_id,
        Task.completed == False,
        Task.due_date < now,
        Task.due_date.isnot(None)
    ).order_by(Task.due_date)

    tasks = session.exec(query).all()

    # Add tags to each task
    result = []
    for task in tasks:
        task_dict = task.model_dump()
        task_tags = session.exec(
            select(Tag).join(TaskTag).where(TaskTag.task_id == task.id)
        ).all()
        task_dict["tags"] = [tag.name for tag in task_tags]
        result.append(TaskRead(**task_dict))

    return result


@router.get("/tasks/search")
def search_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    q: str = Query(..., description="Search query string"),
    limit: int = Query(20, le=100, description="Maximum number of results")
):
    """
    Search tasks by title or description
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    from sqlmodel import or_

    # Build search query
    query = select(Task).where(
        Task.user_id == user_id
    ).where(
        or_(
            Task.title.ilike(f"%{q}%"),
            Task.description.ilike(f"%{q}%")
        )
    ).limit(limit)

    tasks = session.exec(query).all()

    # Add tags to each task
    result = []
    for task in tasks:
        task_dict = task.model_dump()
        task_tags = session.exec(
            select(Tag).join(TaskTag).where(TaskTag.task_id == task.id)
        ).all()
        task_dict["tags"] = [tag.name for tag in task_tags]
        result.append(TaskRead(**task_dict))

    return result


@router.get("/tasks/due_soon")
def get_tasks_due_soon(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    days_ahead: int = Query(7, description="Number of days ahead to include")
):
    """
    Get tasks that are due soon (within specified number of days)
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    now = datetime.utcnow()
    future_limit = now + timedelta(days=days_ahead)

    query = select(Task).where(
        Task.user_id == user_id,
        Task.completed == False,
        Task.due_date >= now,
        Task.due_date <= future_limit,
        Task.due_date.isnot(None)
    ).order_by(Task.due_date)

    tasks = session.exec(query).all()

    # Add tags to each task
    result = []
    for task in tasks:
        task_dict = task.model_dump()
        task_tags = session.exec(
            select(Tag).join(TaskTag).where(TaskTag.task_id == task.id)
        ).all()
        task_dict["tags"] = [tag.name for tag in task_tags]
        result.append(TaskRead(**task_dict))

    return result
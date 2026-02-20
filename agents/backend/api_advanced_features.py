# Task: T5.3.5 - API Endpoints for Advanced Features
# Spec Reference: phase5-spec.md Section 3.2 (Advanced Features)
# Constitution: constitution.md v5.0 Section 4.4
#
# This module provides FastAPI endpoints for:
# - Setting due dates on tasks
# - Configuring reminders
# - Managing recurring tasks
# - Getting recurring tasks list
#
# Version: 1.0
# Date: 2026-02-15

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from ..core.database import get_session
from ..models.task import TaskAdvanced, TaskCreate, TaskUpdate, TaskResponse
from .task_event_publisher import TaskEventPublisher
from .dapr_jobs_integration import ReminderScheduler, RecurringTaskScheduler

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# Initialize event publisher and schedulers
event_publisher = TaskEventPublisher()
reminder_scheduler = ReminderScheduler()
recurring_scheduler = RecurringTaskScheduler()


# Request/Response Models
class DueDateUpdate(BaseModel):
    """Request model for updating task due date"""
    due_date: datetime = Field(description="Task due date in ISO format")


class ReminderUpdate(BaseModel):
    """Request model for updating task reminder"""
    enabled: bool = True
    time_before: str = Field(pattern=r"^\d+[mhdw]$", description="Time before due date (e.g., 1h, 1d)")
    channels: List[str] = Field(default=["email"], description="Notification channels")


class RecurrenceUpdate(BaseModel):
    """Request model for updating task recurrence"""
    enabled: bool = True
    interval: str = Field(description="Recurrence interval: daily, weekly, monthly, custom")
    frequency: int = Field(ge=1, le=365, default=1)
    days: Optional[List[str]] = Field(default=None, description="Days for weekly recurrence")
    end_date: Optional[datetime] = Field(default=None)


# Endpoints

@router.put("/{task_id}/due-date", response_model=TaskResponse)
async def set_due_date(
    task_id: str,
    due_date_update: DueDateUpdate,
    session: Session = Depends(get_session),
    user_id: str = Query(..., description="User ID")
):
    """
    Set or update the due date for a task.

    Args:
        task_id: Task identifier
        due_date_update: Due date update payload
        session: Database session
        user_id: User identifier

    Returns:
        Updated task
    """
    # Get task
    task = session.exec(
        select(TaskAdvanced).where(
            TaskAdvanced.id == task_id,
            TaskAdvanced.user_id == user_id
        )
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update due date
    old_due_date = task.due_date
    task.due_date = due_date_update.due_date
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    # Publish event
    task_dict = task.dict()
    task_dict["created_at"] = task_dict["created_at"].isoformat()
    task_dict["updated_at"] = task_dict["updated_at"].isoformat()
    if task_dict.get("due_date"):
        task_dict["due_date"] = task_dict["due_date"].isoformat()

    event_publisher.publish_task_updated(
        task_dict,
        {"due_date": {"old": old_due_date, "new": due_date_update.due_date}}
    )

    return task


@router.put("/{task_id}/reminder", response_model=TaskResponse)
async def set_reminder(
    task_id: str,
    reminder_update: ReminderUpdate,
    session: Session = Depends(get_session),
    user_id: str = Query(..., description="User ID")
):
    """
    Set or update the reminder configuration for a task.

    Args:
        task_id: Task identifier
        reminder_update: Reminder configuration
        session: Database session
        user_id: User identifier

    Returns:
        Updated task
    """
    # Get task
    task = session.exec(
        select(TaskAdvanced).where(
            TaskAdvanced.id == task_id,
            TaskAdvanced.user_id == user_id
        )
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.due_date:
        raise HTTPException(
            status_code=400,
            detail="Cannot set reminder without due date. Set due date first."
        )

    # Update reminder
    old_reminder = task.reminder
    task.reminder = reminder_update.dict()
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    # Schedule reminder via Dapr Jobs API
    if reminder_update.enabled:
        reminder_scheduler.schedule_reminder(
            task_id=task.id,
            task_title=task.title,
            due_date=task.due_date,
            time_before=reminder_update.time_before,
            channels=reminder_update.channels,
            user_id=user_id
        )
    else:
        # Cancel existing reminder
        reminder_scheduler.cancel_reminder(task_id)

    # Publish event
    task_dict = task.dict()
    task_dict["created_at"] = task_dict["created_at"].isoformat()
    task_dict["updated_at"] = task_dict["updated_at"].isoformat()
    if task_dict.get("due_date"):
        task_dict["due_date"] = task_dict["due_date"].isoformat()

    event_publisher.publish_task_updated(
        task_dict,
        {"reminder": {"old": old_reminder, "new": task.reminder}}
    )

    return task


@router.put("/{task_id}/recurrence", response_model=TaskResponse)
async def set_recurrence(
    task_id: str,
    recurrence_update: RecurrenceUpdate,
    session: Session = Depends(get_session),
    user_id: str = Query(..., description="User ID")
):
    """
    Set or update the recurrence configuration for a task.

    Args:
        task_id: Task identifier
        recurrence_update: Recurrence configuration
        session: Database session
        user_id: User identifier

    Returns:
        Updated task
    """
    # Get task
    task = session.exec(
        select(TaskAdvanced).where(
            TaskAdvanced.id == task_id,
            TaskAdvanced.user_id == user_id
        )
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update recurrence
    old_recurrence = task.recurrence
    task.recurrence = recurrence_update.dict()
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    # Schedule next occurrence if enabled
    if recurrence_update.enabled:
        task_data = {
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "tags": task.tags,
            "user_id": user_id
        }
        recurring_scheduler.schedule_next_occurrence(
            parent_task_id=task.id,
            task_data=task_data,
            recurrence_config=task.recurrence
        )
    else:
        # Cancel existing recurrence
        recurring_scheduler.cancel_recurrence(task_id)

    # Publish event
    task_dict = task.dict()
    task_dict["created_at"] = task_dict["created_at"].isoformat()
    task_dict["updated_at"] = task_dict["updated_at"].isoformat()
    if task_dict.get("due_date"):
        task_dict["due_date"] = task_dict["due_date"].isoformat()

    event_publisher.publish_task_updated(
        task_dict,
        {"recurrence": {"old": old_recurrence, "new": task.recurrence}}
    )

    return task


@router.delete("/{task_id}/recurrence", response_model=TaskResponse)
async def delete_recurrence(
    task_id: str,
    session: Session = Depends(get_session),
    user_id: str = Query(..., description="User ID")
):
    """
    Stop recurrence for a task.

    Args:
        task_id: Task identifier
        session: Database session
        user_id: User identifier

    Returns:
        Updated task
    """
    # Get task
    task = session.exec(
        select(TaskAdvanced).where(
            TaskAdvanced.id == task_id,
            TaskAdvanced.user_id == user_id
        )
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Remove recurrence
    task.recurrence = None
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    # Cancel scheduled recurrence
    recurring_scheduler.cancel_recurrence(task_id)

    # Publish event
    task_dict = task.dict()
    task_dict["created_at"] = task_dict["created_at"].isoformat()
    task_dict["updated_at"] = task_dict["updated_at"].isoformat()

    event_publisher.publish_task_updated(
        task_dict,
        {"recurrence": {"old": task.recurrence, "new": None}}
    )

    return task


@router.get("/recurring", response_model=List[TaskResponse])
async def get_recurring_tasks(
    session: Session = Depends(get_session),
    user_id: str = Query(..., description="User ID")
):
    """
    Get all recurring tasks for a user.

    Args:
        session: Database session
        user_id: User identifier

    Returns:
        List of recurring tasks
    """
    tasks = session.exec(
        select(TaskAdvanced).where(
            TaskAdvanced.user_id == user_id,
            TaskAdvanced.recurrence.isnot(None)
        )
    ).all()

    return tasks


@router.get("/{task_id}/instances", response_model=List[TaskResponse])
async def get_task_instances(
    task_id: str,
    session: Session = Depends(get_session),
    user_id: str = Query(..., description="User ID")
):
    """
    Get all instances of a recurring task.

    Args:
        task_id: Parent task identifier
        session: Database session
        user_id: User identifier

    Returns:
        List of task instances
    """
    # Get parent task
    parent_task = session.exec(
        select(TaskAdvanced).where(
            TaskAdvanced.id == task_id,
            TaskAdvanced.user_id == user_id
        )
    ).first()

    if not parent_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get all instances
    instances = session.exec(
        select(TaskAdvanced).where(
            TaskAdvanced.parent_task_id == task_id,
            TaskAdvanced.user_id == user_id
        )
    ).all()

    return [parent_task] + list(instances)

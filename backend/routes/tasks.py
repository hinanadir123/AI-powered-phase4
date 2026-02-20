from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, desc, asc, or_, and_, col
from typing import List, Optional
from datetime import datetime
from models import Task, Tag, TaskTag
from schemas import TaskCreate, TaskUpdate, TaskRead
from db import get_session
from dependencies import get_current_user
from services.recurrence_service import RecurrenceService
from services.reminder_service import ReminderService
from agents.recurring_tasks_service import RecurringTaskService
from agents.dapr_jobs_integration import job_scheduler
from event_publisher import event_publisher

router = APIRouter(prefix="/api/{user_id}", tags=["tasks"])


@router.get("/tasks", response_model=List[TaskRead])
def get_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    status_param: str = Query("all", regex="^(all|pending|completed)$"),
    sort: str = Query("created_at:desc"),
    # Phase 5 filters
    priority: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    due_from: Optional[datetime] = Query(None),
    due_to: Optional[datetime] = Query(None),
    # Phase 6 advanced filters
    recurring_only: bool = Query(False, description="Return only recurring tasks"),
    overdue: bool = Query(False, description="Filter for overdue tasks"),
    due_before: Optional[datetime] = Query(None, description="Filter tasks due before this datetime")
):
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    # Build query based on status filter
    query = select(Task).where(Task.user_id == user_id)

    if status_param == "pending":
        query = query.where(Task.completed == False)
    elif status_param == "completed":
        query = query.where(Task.completed == True)

    # Phase 5: Priority filter
    if priority:
        query = query.where(Task.priority == priority)

    # Phase 5: Search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )

    # Phase 5: Due date range filter
    if due_from:
        query = query.where(Task.due_date >= due_from)
    if due_to:
        query = query.where(Task.due_date <= due_to)

    # Phase 6: Additional due date filters
    if due_before:
        query = query.where(Task.due_date <= due_before)

    # Phase 6: Overdue filter
    if overdue:
        now = datetime.utcnow()
        query = query.where(
            Task.completed == False,
            Task.due_date < now,
            Task.due_date.isnot(None)
        )

    # Phase 6: Recurring filter
    if recurring_only:
        query = query.where(Task.recurrence_pattern.isnot(None))

    # Phase 5: Tag filter
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        query = query.join(TaskTag).join(Tag).where(col(Tag.name).in_(tag_list))

    # Phase 5: Enhanced sorting
    sort_parts = sort.split(":")
    sort_field = sort_parts[0] if len(sort_parts) > 0 else "created_at"
    sort_direction = sort_parts[1] if len(sort_parts) > 1 else "desc"

    if sort_field == "title":
        query = query.order_by(asc(Task.title) if sort_direction == "asc" else desc(Task.title))
    elif sort_field == "priority":
        query = query.order_by(asc(Task.priority) if sort_direction == "asc" else desc(Task.priority))
    elif sort_field == "due_date":
        query = query.order_by(asc(Task.due_date) if sort_direction == "asc" else desc(Task.due_date))
    else:  # Default to created_at
        query = query.order_by(asc(Task.created_at) if sort_direction == "asc" else desc(Task.created_at))

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


@router.post("/tasks", response_model=TaskRead)
def create_task(
    user_id: str,
    task: TaskCreate,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)):
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    # Validate title length
    if len(task.title) < 1 or len(task.title) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be between 1 and 200 characters"
        )

    # Create task with Phase 5 fields
    db_task = Task(
        title=task.title,
        description=task.description,
        user_id=user_id,
        completed=False,
        priority=task.priority or "medium",
        due_date=task.due_date,
        reminder_time=task.reminder_time,
        recurrence_pattern=task.recurrence_pattern,
        recurrence_end_date=task.recurrence_end_date
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Handle tags if provided
    if task.tags:
        for tag_name in task.tags:
            # Get or create tag
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.commit()
                session.refresh(tag)

            # Create task-tag association
            task_tag = TaskTag(task_id=db_task.id, tag_id=tag.id)
            session.add(task_tag)

        session.commit()
        session.refresh(db_task)

    # Return task with tags
    task_dict = db_task.model_dump()
    task_tags = session.exec(
        select(Tag).join(TaskTag).where(TaskTag.task_id == db_task.id)
    ).all()
    task_dict["tags"] = [tag.name for tag in task_tags]

    # Publish task created event to Kafka via Dapr
    event_publisher.publish_task_created(db_task.id, task_dict)

    # If reminder is set, schedule it via Dapr Jobs
    if db_task.reminder_time:
        success = job_scheduler.schedule_task_reminder(
            task_id=db_task.id,
            user_id=db_task.user_id,
            reminder_time=db_task.reminder_time,
            task_title=db_task.title,
            task_priority=db_task.priority,
            task_description=db_task.description or ""
        )
        if success:
            print(f"[REMINDER] Scheduled reminder for task {db_task.id}")
        else:
            print(f"[REMINDER] Failed to schedule reminder for task {db_task.id}")

    # If this is a recurring task, schedule next instance
    if db_task.recurrence_pattern:
        success = job_scheduler.schedule_recurring_task_instance_creation(
            parent_task_id=db_task.id,
            user_id=db_task.user_id,
            cron_expression=db_task.recurrence_pattern,
            title=db_task.title
        )
        if success:
            print(f"[RECURRING] Scheduled job for creating instances of task {db_task.id}")
        else:
            print(f"[RECURRING] Failed to schedule recurring job for task {db_task.id}")

    return TaskRead(**task_dict)


@router.get("/tasks/{id}", response_model=TaskRead)
def get_task(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)):
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify that the task belongs to the user
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: task does not belong to user"
        )

    # Return task with tags
    task_dict = task.model_dump()
    task_tags = session.exec(
        select(Tag).join(TaskTag).where(TaskTag.task_id == task.id)
    ).all()
    task_dict["tags"] = [tag.name for tag in task_tags]

    return TaskRead(**task_dict)


@router.put("/tasks/{id}", response_model=TaskRead)
def update_task(
    user_id: str,
    id: int,
    task_update: TaskUpdate,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)):
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    db_task = session.get(Task, id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify that the task belongs to the user
    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: task does not belong to user"
        )

    # Update fields if provided
    if task_update.title is not None:
        if len(task_update.title) < 1 or len(task_update.title) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title must be between 1 and 200 characters"
            )
        db_task.title = task_update.title

    if task_update.description is not None:
        db_task.description = task_update.description

    if task_update.completed is not None:
        db_task.completed = task_update.completed

    # Phase 5 fields
    if task_update.priority is not None:
        db_task.priority = task_update.priority

    if task_update.due_date is not None:
        db_task.due_date = task_update.due_date

    if task_update.reminder_time is not None:
        db_task.reminder_time = task_update.reminder_time

    if task_update.recurrence_pattern is not None:
        db_task.recurrence_pattern = task_update.recurrence_pattern

    if task_update.recurrence_end_date is not None:
        db_task.recurrence_end_date = task_update.recurrence_end_date

    # Handle tags update
    if task_update.tags is not None:
        # Remove existing tags
        existing_task_tags = session.exec(
            select(TaskTag).where(TaskTag.task_id == db_task.id)
        ).all()
        for task_tag in existing_task_tags:
            session.delete(task_tag)
        session.commit()

        # Add new tags
        for tag_name in task_update.tags:
            tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.commit()
                session.refresh(tag)

            task_tag = TaskTag(task_id=db_task.id, tag_id=tag.id)
            session.add(task_tag)

    db_task.updated_at = datetime.utcnow()
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Return task with tags
    task_dict = db_task.model_dump()
    task_tags = session.exec(
        select(Tag).join(TaskTag).where(TaskTag.task_id == db_task.id)
    ).all()
    task_dict["tags"] = [tag.name for tag in task_tags]

    # Publish task updated event to Kafka via Dapr
    changes = task_update.model_dump(exclude_unset=True)
    event_publisher.publish_task_updated(db_task.id, task_dict, changes)

    # If reminder time was updated, schedule new job via Dapr Jobs
    if task_update.reminder_time is not None:
        # Cancel any existing scheduled reminder
        # In a real implementation, we'd have a way to track job IDs
        print(f"[REMINDER] Reminder time updated for task {db_task.id}")
        # Schedule new reminder if not empty
        if db_task.reminder_time:
            success = job_scheduler.schedule_task_reminder(
                task_id=db_task.id,
                user_id=db_task.user_id,
                reminder_time=db_task.reminder_time,
                task_title=db_task.title,
                task_priority=db_task.priority,
                task_description=db_task.description or ""
            )
            if success:
                print(f"[REMINDER] Rescheduled reminder for task {db_task.id}")
            else:
                print(f"[REMINDER] Failed to reschedule reminder for task {db_task.id}")

    # If recurrence pattern was updated, update job scheduling
    if task_update.recurrence_pattern is not None and db_task.recurrence_pattern:
        success = job_scheduler.schedule_recurring_task_instance_creation(
            parent_task_id=db_task.id,
            user_id=db_task.user_id,
            cron_expression=db_task.recurrence_pattern,
            title=db_task.title
        )
        if success:
            print(f"[RECURRING] Updated schedule for recurring task {db_task.id}")
        else:
            print(f"[RECURRING] Failed to update schedule for recurring task {db_task.id}")

    return TaskRead(**task_dict)


@router.delete("/tasks/{id}")
def delete_task(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)):
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    db_task = session.get(Task, id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify that the task belongs to the user
    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: task does not belong to user"
        )

    # Publish task deleted event before deleting
    event_publisher.publish_task_deleted(db_task.id, user_id)

    session.delete(db_task)
    session.commit()
    return {"message": "Task deleted successfully"}


@router.patch("/tasks/{id}/complete", response_model=TaskRead)
def toggle_task_complete(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)):
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    db_task = session.get(Task, id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify that the task belongs to the user
    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: task does not belong to user"
        )

    # Toggle the completed status
    db_task.completed = not db_task.completed
    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Return task with tags
    task_dict = db_task.model_dump()
    task_tags = session.exec(
        select(Tag).join(TaskTag).where(TaskTag.task_id == db_task.id)
    ).all()
    task_dict["tags"] = [tag.name for tag in task_tags]

    # Publish task completed event if task was marked as completed
    if db_task.completed:
        event_publisher.publish_task_completed(db_task.id, task_dict)

    return TaskRead(**task_dict)


# Phase 5: Tags endpoint
@router.get("/tags")
def get_tags(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all available tags for the user's tasks"""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    # Get all unique tags used by the user's tasks
    tags = session.exec(
        select(Tag)
        .join(TaskTag)
        .join(Task)
        .where(Task.user_id == user_id)
        .distinct()
    ).all()

    return [{"id": tag.id, "name": tag.name} for tag in tags]


# Phase 5 Advanced: Complete recurring task and create next instance
@router.post("/tasks/{id}/complete-recurring", response_model=TaskRead)
def complete_recurring_task(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Complete a recurring task and create the next instance"""
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

    # Mark task as completed
    db_task.completed = True
    db_task.updated_at = datetime.utcnow()
    session.add(db_task)
    session.commit()

    # Create next instance if recurring
    if db_task.recurrence_pattern:
        next_task = RecurrenceService.create_next_instance(session, db_task)
        if next_task:
            print(f"Created next recurring instance: {next_task.id}")

    session.refresh(db_task)

    # Return completed task with tags
    task_dict = db_task.model_dump()
    task_tags = session.exec(
        select(Tag).join(TaskTag).where(TaskTag.task_id == db_task.id)
    ).all()
    task_dict["tags"] = [tag.name for tag in task_tags]

    return TaskRead(**task_dict)


# Phase 5 Advanced: Get overdue tasks
@router.get("/tasks/overdue", response_model=List[TaskRead])
def get_overdue_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all overdue tasks for the user"""
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


# Phase 5 Advanced: Process pending reminders (manual trigger)
@router.post("/reminders/process")
def process_reminders(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Manually trigger reminder processing"""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    count = ReminderService.process_reminders(session)
    return {"message": f"Processed {count} reminders"}


# Phase 5 Advanced: Get upcoming recurring instances
@router.get("/tasks/{id}/recurring-instances", response_model=List[TaskRead])
def get_recurring_instances(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get upcoming instances of a recurring task"""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    # Verify parent task exists and belongs to user
    parent_task = session.get(Task, id)
    if not parent_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if parent_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: task does not belong to user"
        )

    instances = RecurrenceService.get_upcoming_instances(session, id)

    # Add tags to each instance
    result = []
    for task in instances:
        task_dict = task.model_dump()
        task_tags = session.exec(
            select(Tag).join(TaskTag).where(TaskTag.task_id == task.id)
        ).all()
        task_dict["tags"] = [tag.name for tag in task_tags]
        result.append(TaskRead(**task_dict))

    return result
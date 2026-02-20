"""
Advanced Task Management API Endpoints
Task: Implement GET /tasks/recurring and GET /tasks/search endpoints
Spec Reference: phase5-spec.md Section 3.2 (Advanced Features)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timedelta
from models import Task, Tag, TaskTag
from schemas import TaskRead
from db import get_session
from dependencies import get_current_user
from services.recurrence_service import RecurrenceService
from agents.recurring_tasks_service import RecurringTaskService


router = APIRouter(prefix="/api/{user_id}", tags=["advanced-tasks"])


@router.get("/tasks/recurring")
def get_recurring_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    active_only: bool = Query(True, description="Return only currently active recurring tasks"),
    limit: int = Query(20, ge=1, le=100, description="Limit number of results")
):
    """
    Get all recurring tasks for the user

    Args:
        user_id: ID of the user
        current_user_id: ID from authentication
        session: Database session
        active_only: Only return recurring tasks that haven't reached end date
        limit: Maximum number of tasks to return

    Returns:
        List of recurring tasks for the user
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    # Query for tasks that have recurrence pattern
    query = select(Task).where(
        Task.user_id == user_id,
        Task.recurrence_pattern.isnot(None)  # Not null recurrence pattern
    ).order_by(Task.created_at.desc()).limit(limit)

    recurring_tasks = session.exec(query).all()

    # Filter active recurring tasks based on recurrence_end_date if required
    if active_only:
        now = datetime.utcnow()
        recurring_tasks = [
            task for task in recurring_tasks
            if not task.recurrence_end_date or task.recurrence_end_date > now
        ]

    # Add tags to each task
    result = []
    for task in recurring_tasks:
        task_dict = task.model_dump()

        # Get associated tags
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
    q: str = Query(..., description="Search query - supports title, description, and tag matching"),
    search_tags: bool = Query(True, description="Whether to include tags in the search"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    due_after: Optional[datetime] = Query(None, description="Filter tasks due after this date"),
    due_before: Optional[datetime] = Query(None, description="Filter tasks due before this date"),
    limit: int = Query(50, ge=1, le=100, description="Limit number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Advanced search for tasks

    Args:
        user_id: ID of the user
        current_user_id: ID from authentication
        session: Database session
        q: Search query string
        search_tags: Whether to search within tags
        completed: Filter by completion status
        priority: Filter by priority
        due_after: Filter tasks due after this date
        due_before: Filter tasks due before this date
        limit: Maximum number of results
        offset: Pagination offset

    Returns:
        List of matching tasks with search highlights
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    from sqlmodel import or_, and_, col

    # Initial query for user's tasks
    query = select(Task).where(Task.user_id == user_id)

    # Create full-text search condition
    search_pattern = f"%{q}%"
    search_conditions = [
        Task.title.ilike(search_pattern),
        Task.description.ilike(search_pattern)
    ]

    # Add tag search if required
    if search_tags:
        # Search for tasks associated with tags matching the query
        tag_query = select(TaskTag.task_id).join(Tag).where(
            Tag.name.ilike(search_pattern)
        )
        tag_task_ids = session.exec(tag_query).all()
        search_conditions.append(Task.id.in_(tag_task_ids))

    # Apply search filter
    query = query.where(or_(*search_conditions))

    # Apply filters
    if completed is not None:
        query = query.where(Task.completed == completed)

    if priority is not None:
        query = query.where(Task.priority == priority)

    if due_after is not None:
        query = query.where(Task.due_date >= due_after)

    if due_before is not None:
        query = query.where(Task.due_date <= due_before)

    # Apply ordering and pagination
    query = query.order_by(Task.created_at.desc()).offset(offset).limit(limit)

    # Execute query
    search_results = session.exec(query).all()

    # Add tags to each task
    result = []
    for task in search_results:
        task_dict = task.model_dump()

        # Get associated tags
        task_tags = session.exec(
            select(Tag).join(TaskTag).where(TaskTag.task_id == task.id)
        ).all()

        task_dict["tags"] = [tag.name for tag in task_tags]
        result.append(TaskRead(**task_dict))

    return result


@router.get("/tasks/upcoming")
def get_upcoming_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    days_ahead: int = Query(7, ge=1, le=30, description="Number of days to look ahead"),
    include_recurring: bool = Query(True, description="Include recurring tasks that will have instances in the period")
):
    """
    Get tasks due within the specified number of days

    Args:
        user_id: ID of the user
        current_user_id: ID from authentication
        session: Database session
        days_ahead: Number of days to look ahead
        include_recurring: Whether to include recurring tasks

    Returns:
        List of upcoming tasks
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
        Task.completed == False,  # Only incomplete tasks
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

    # Add recurring instances if requested
    if include_recurring:
        # Get recurring tasks that will have instances in the specified period
        recurring_query = select(Task).where(
            Task.user_id == user_id,
            Task.completed == False,
            Task.recurrence_pattern.isnot(None)
        )

        recurring_tasks = session.exec(recurring_query).all()

        for recurring_task in recurring_tasks:
            # Calculate next few occurrences within the time period
            occurrences = RecurringTaskService.get_next_occurrences(
                session,
                recurring_task.id,
                count=10,  # Get up to 10 future instances
                start_from=now
            )

            # Add only occurrences within our window
            for occurrence in occurrences:
                if occurrence <= future_limit:
                    task_dict = recurring_task.model_dump()
                    # Create a representation for this occurrence
                    occurrence_task = TaskRead(
                        **{**task_dict,
                           "due_date": occurrence,
                           "title": f"{task_dict['title']} (Recurring Instance)"}
                    )
                    result.append(occurrence_task)

    # Sort again as we added recurring instances
    result.sort(key=lambda x: x.due_date or datetime.max)

    return result


@router.get("/tasks/overdue")
def get_overdue_tasks_with_options(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    priority_filter: Optional[str] = Query(None, description="Filter overdue tasks by priority"),
    include_tags: bool = Query(True, description="Include tags in results")
):
    """
    Extended overdue tasks endpoint with additional filtering options

    Args:
        user_id: ID of the user
        current_user_id: ID from authentication
        session: Database session
        priority_filter: Optional priority filter for overdue tasks
        include_tags: Whether to include tags in results

    Returns:
        List of overdue tasks with specified filters
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    now = datetime.utcnow()
    query = select(Task).where(
        Task.user_id == user_id,
        Task.completed == False,  # Only incomplete tasks
        Task.due_date < now,  # Due date in the past
        Task.due_date.isnot(None)
    ).order_by(Task.due_date.desc())  # Oldest first

    # Apply priority filter if specified
    if priority_filter:
        query = query.where(Task.priority == priority_filter)

    tasks = session.exec(query).all()

    result = []
    for task in tasks:
        task_dict = task.model_dump()

        if include_tags:
            task_tags = session.exec(
                select(Tag).join(TaskTag).where(TaskTag.task_id == task.id)
            ).all()
            task_dict["tags"] = [tag.name for tag in task_tags]

        result.append(TaskRead(**task_dict))

    return result


@router.get("/tasks/stats")
def get_task_statistics(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get statistics about tasks

    Args:
        user_id: ID of the user
        current_user_id: ID from authentication
        session: Database session

    Returns:
        Task statistics
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    now = datetime.utcnow()

    # Total tasks
    total_query = select(Task).where(Task.user_id == user_id)
    total_count = len(session.exec(total_query).all())

    # Completed tasks
    completed_query = select(Task).where(
        Task.user_id == user_id,
        Task.completed == True
    )
    completed_count = len(session.exec(completed_query).all())

    # Overdue tasks
    overdue_query = select(Task).where(
        Task.user_id == user_id,
        Task.completed == False,
        Task.due_date < now,
        Task.due_date.isnot(None)
    )
    overdue_count = len(session.exec(overdue_query).all())

    # Upcoming tasks (due in next 7 days)
    upcoming_limit = now + timedelta(days=7)
    upcoming_query = select(Task).where(
        Task.user_id == user_id,
        Task.completed == False,
        Task.due_date >= now,
        Task.due_date <= upcoming_limit,
        Task.due_date.isnot(None)
    )
    upcoming_count = len(session.exec(upcoming_query).all())

    # Recurring tasks
    recurring_query = select(Task).where(
        Task.user_id == user_id,
        Task.recurrence_pattern.isnot(None)
    )
    recurring_count = len(session.exec(recurring_query).all())

    return {
        "total": total_count,
        "completed": completed_count,
        "pending": total_count - completed_count,
        "overdue": overdue_count,
        "upcoming": upcoming_count,
        "recurring": recurring_count,
        "on_time_rate": (completed_count / total_count * 100) if total_count > 0 else 0
    }


@router.post("/tasks/batch/process")
def process_tasks_batch(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    task_ids: List[int] = Query(..., description="List of task IDs to process"),
    action: str = Query(..., regex="^(complete|delete|clear-reminders)$", description="Action to perform on tasks")
):
    """
    Batch process multiple tasks

    Args:
        user_id: ID of the user
        current_user_id: ID from authentication
        session: Database session
        task_ids: List of task IDs to process
        action: Action to perform (complete, delete, clear-reminders)

    Returns:
        Confirmation of batch processing
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    # Get all the tasks
    tasks_query = select(Task).where(
        Task.id.in_(task_ids),
        Task.user_id == user_id
    )
    tasks = session.exec(tasks_query).all()

    # Validate all tasks belong to user
    if len(tasks) != len(task_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more tasks not found or do not belong to user"
        )

    processed_count = 0

    for task in tasks:
        if action == "complete":
            task.completed = True
            task.updated_at = datetime.utcnow()
            processed_count += 1
        elif action == "delete":
            session.delete(task)
            processed_count += 1
        elif action == "clear-reminders":
            task.reminder_time = None
            task.updated_at = datetime.utcnow()
            processed_count += 1

        # Commit changes for each task
        session.add(task)

    session.commit()
    return {
        "message": f"Successfully processed {processed_count} tasks",
        "action": action,
        "processed_count": processed_count
    }
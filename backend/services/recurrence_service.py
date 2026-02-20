"""
Recurrence Service for handling recurring task logic
Phase 5 - Advanced Features
"""

from datetime import datetime, timedelta
from typing import Optional, List
from models import Task, RecurrencePattern
from sqlmodel import Session


class RecurrenceService:
    """Service for managing recurring tasks"""

    @staticmethod
    def calculate_next_occurrence(
        current_date: datetime,
        pattern: str,
        end_date: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Calculate the next occurrence date based on recurrence pattern

        Args:
            current_date: Current task due date
            pattern: Recurrence pattern (daily, weekly, monthly, yearly)
            end_date: Optional end date for recurrence

        Returns:
            Next occurrence date or None if recurrence has ended
        """
        if not pattern or pattern not in ['daily', 'weekly', 'monthly', 'yearly']:
            return None

        # Calculate next date based on pattern
        if pattern == 'daily':
            next_date = current_date + timedelta(days=1)
        elif pattern == 'weekly':
            next_date = current_date + timedelta(weeks=1)
        elif pattern == 'monthly':
            # Add one month (approximate - handle edge cases)
            next_date = current_date + timedelta(days=30)
        elif pattern == 'yearly':
            next_date = current_date + timedelta(days=365)
        else:
            return None

        # Check if next date exceeds end date
        if end_date and next_date > end_date:
            return None

        return next_date

    @staticmethod
    def create_next_instance(
        session: Session,
        parent_task: Task
    ) -> Optional[Task]:
        """
        Create the next instance of a recurring task

        Args:
            session: Database session
            parent_task: Parent task with recurrence pattern

        Returns:
            New task instance or None if recurrence has ended
        """
        if not parent_task.recurrence_pattern or not parent_task.due_date:
            return None

        # Calculate next occurrence
        next_due_date = RecurrenceService.calculate_next_occurrence(
            parent_task.due_date,
            parent_task.recurrence_pattern,
            parent_task.recurrence_end_date
        )

        if not next_due_date:
            return None

        # Create new task instance
        new_task = Task(
            title=parent_task.title,
            description=parent_task.description,
            user_id=parent_task.user_id,
            priority=parent_task.priority,
            due_date=next_due_date,
            reminder_time=parent_task.reminder_time,
            recurrence_pattern=parent_task.recurrence_pattern,
            recurrence_end_date=parent_task.recurrence_end_date,
            parent_task_id=parent_task.id,
            completed=False
        )

        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return new_task

    @staticmethod
    def get_upcoming_instances(
        session: Session,
        parent_task_id: int,
        limit: int = 10
    ) -> List[Task]:
        """
        Get upcoming instances of a recurring task

        Args:
            session: Database session
            parent_task_id: Parent task ID
            limit: Maximum number of instances to return

        Returns:
            List of upcoming task instances
        """
        from sqlmodel import select

        query = select(Task).where(
            Task.parent_task_id == parent_task_id,
            Task.completed == False
        ).order_by(Task.due_date).limit(limit)

        return list(session.exec(query).all())

    @staticmethod
    def is_overdue(task: Task) -> bool:
        """
        Check if a task is overdue

        Args:
            task: Task to check

        Returns:
            True if task is overdue, False otherwise
        """
        if not task.due_date or task.completed:
            return False

        return datetime.utcnow() > task.due_date

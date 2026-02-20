"""
Recurring Tasks Service with Cron Expression Support
Task: T5.3.1 - Implements recurring task logic with cron expressions
Spec Reference: phase5-spec.md Section 3.2.1 (Recurring Tasks)
Constitution: constitution.md v5.0
"""
from datetime import datetime, timedelta
import croniter
from typing import Optional, Dict, Any, List
from sqlmodel import Session, select
from models import Task
from event_publisher import event_publisher


class RecurringTaskService:
    """
    Advanced Recurring Task Service with Cron Expression Support
    """

    @staticmethod
    def parse_recurrence_pattern(recurrence_info: Dict[str, Any]) -> Optional[str]:
        """
        Parse recurrence pattern and return appropriate cron expression

        Args:
            recurrence_info: Dictionary containing recurrence configuration

        Returns:
            str: Cron expression or None if invalid configuration
        """
        pattern = recurrence_info.get('pattern', recurrence_info.get('interval', ''))
        frequency = recurrence_info.get('frequency', 1)

        if pattern == 'daily':
            return f"0 0 */{max(1, frequency)} * *"
        elif pattern == 'weekly':
            days = recurrence_info.get('days', ['monday'])
            # Convert day names to numbers (0=Sunday, 1=Monday, etc.)
            day_map = {
                'sunday': 0, 'monday': 1, 'tuesday': 2, 'wednesday': 3,
                'thursday': 4, 'friday': 5, 'saturday': 6
            }
            day_numbers = [day_map.get(day.lower(), 1) for day in days]
            day_cron = ','.join(map(str, day_numbers))
            return f"0 0 * * {day_cron}"
        elif pattern == 'monthly':
            # Day of month (1-31)
            day_of_month = recurrence_info.get('day', 1)
            return f"0 0 {min(31, max(1, day_of_month))} */{max(1, frequency)} *"
        elif pattern == 'yearly':
            # Day of year (1-365)
            month = recurrence_info.get('month', 1)
            day = recurrence_info.get('day', 1)
            return f"0 0 {min(31, max(1, day))} {min(12, max(1, month))} *"
        elif 'cron_expression' in recurrence_info:
            # User-provided cron expression
            return recurrence_info['cron_expression']
        else:
            return None

    @staticmethod
    def calculate_next_occurrence_from_cron(
        cron_expression: str,
        current_time: datetime = None
    ) -> Optional[datetime]:
        """
        Calculate next occurrence using cron expression

        Args:
            cron_expression: Valid cron expression
            current_time: Reference time (defaults to now)

        Returns:
            datetime: Next occurrence or None if invalid
        """
        if current_time is None:
            current_time = datetime.utcnow()

        try:
            cron_iter = croniter.croniter(cron_expression, current_time)
            next_time = cron_iter.get_next(datetime)
            return next_time
        except Exception:
            return None

    @staticmethod
    def create_next_instance(
        session: Session,
        parent_task: Task,
        scheduled_time: datetime = None
    ) -> Optional[Task]:
        """
        Create next instance of recurring task

        Args:
            session: Database session
            parent_task: Parent task to base recurrence on
            scheduled_time: Specifically scheduled next occurrence time

        Returns:
            Task: New created task or None if recurrence should end
        """
        # Check if recurrence has an end date
        if parent_task.recurrence_end_date and scheduled_time and scheduled_time > parent_task.recurrence_end_date:
            print(f"[RECURRING] Recurrence ended for task {parent_task.id}")
            return None

        if (parent_task.recurrence_end_date and
            datetime.utcnow() > parent_task.recurrence_end_date):
            print(f"[RECURRING] Recurrence ended for task {parent_task.id}")
            return None

        # Define the recurrence structure (simplified version)
        try:
            # Try to parse as JSON structure (full recurrence object)
            import json
            recurrence_obj = json.loads(parent_task.recurrence_pattern)
            pattern = recurrence_obj.get('pattern', 'daily')
            cron_expr = RecurringTaskService.parse_recurrence_pattern(recurrence_obj)
        except (json.JSONDecodeError, TypeError):
            # Fallback to simple string pattern
            pattern = parent_task.recurrence_pattern
            if pattern in ['daily', 'weekly', 'monthly', 'yearly']:
                cron_expr = RecurringTaskService.parse_recurrence_pattern({'pattern': pattern})
            else:
                # Assume it's already a cron expression
                cron_expr = parent_task.recurrence_pattern

        # Calculate next occurrence if not provided
        next_due_date = scheduled_time
        if next_due_date is None and cron_expr:
            next_due_date = RecurringTaskService.calculate_next_occurrence_from_cron(cron_expr)

        # Create new task instance
        new_task = Task(
            title=parent_task.title,
            description=parent_task.description,
            user_id=parent_task.user_id,
            completed=False,
            priority=parent_task.priority,
            due_date=next_due_date,
            # Calculate reminder time based on due date
            reminder_time=next_due_date - timedelta(hours=1) if next_due_date else None,  # Default 1 hour before due date
            recurrence_pattern=parent_task.recurrence_pattern,
            recurrence_end_date=parent_task.recurrence_end_date,
            parent_task_id=parent_task.id  # Reference back to main recurring task
        )

        # Add to database
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        # Publish Kafka event
        event_publisher.publish_recurring_instance_created(
            parent_task_id=parent_task.id,
            new_task_id=new_task.id,
            task_data=new_task.model_dump()
        )

        print(f"[RECURRING] Created next instance for task {parent_task.title}, new task ID: {new_task.id}")
        return new_task

    @staticmethod
    def get_next_occurrences(
        session: Session,
        parent_task_id: int,
        count: int = 5,
        start_from: datetime = None
    ) -> List[datetime]:
        """
        Calculate multiple next occurrences for a recurring task

        Args:
            session: Database session
            parent_task_id: ID of parent recurring task
            count: Number of occurrences to calculate
            start_from: Reference time for calculation

        Returns:
            List[datetime]: List of next occurrence times
        """
        parent_task = session.get(Task, parent_task_id)
        if not parent_task or not parent_task.recurrence_pattern:
            return []

        # Parse recurrence pattern
        try:
            import json
            recurrence_obj = json.loads(parent_task.recurrence_pattern)
            cron_expr = RecurringTaskService.parse_recurrence_pattern(recurrence_obj)
        except (json.JSONDecodeError, TypeError):
            # Fallback to simple pattern
            if parent_task.recurrence_pattern in ['daily', 'weekly', 'monthly', 'yearly']:
                cron_expr = RecurringTaskService.parse_recurrence_pattern({'pattern': parent_task.recurrence_pattern})
            else:
                cron_expr = parent_task.recurrence_pattern

        if not cron_expr:
            return []

        # Calculate occurrences
        if start_from is None:
            start_from = parent_task.due_date or datetime.utcnow()

        occurrences = []
        try:
            cron_iter = croniter.croniter(cron_expr, start_from)
            for _ in range(count):
                next_occ = cron_iter.get_next(datetime)
                if (parent_task.recurrence_end_date and
                    next_occ > parent_task.recurrence_end_date):
                    break
                occurrences.append(next_occ)
        except Exception as e:
            print(f"[RECURRING] Error calculating occurrences: {e}")

        return occurrences

    @staticmethod
    def update_recurrence_pattern(
        session: Session,
        task_id: int,
        recurrence_config: Dict[str, Any]
    ) -> bool:
        """
        Update recurrence pattern for a task

        Args:
            session: Database session
            task_id: Task ID to update
            recurrence_config: New recurrence configuration

        Returns:
            bool: True if update successful
        """
        task = session.get(Task, task_id)
        if not task:
            return False

        # Validate recurrence pattern
        pattern = recurrence_config.get('pattern', recurrence_config.get('interval', ''))
        if pattern not in ['daily', 'weekly', 'monthly', 'yearly'] and 'cron_expression' not in recurrence_config:
            return False  # Invalid pattern

        # Convert config to string for storage
        import json
        task.recurrence_pattern = json.dumps(recurrence_config)

        # Store additional fields if provided
        if 'end_date' in recurrence_config:
            task.recurrence_end_date = recurrence_config['end_date']

        session.add(task)
        session.commit()

        # Emit event
        event_publisher.publish_event(
            topic="task-events",
            event_type="task.recurrence.updated",
            data={
                "task_id": task_id,
                "recurrence_config": recurrence_config,
                "user_id": task.user_id
            }
        )

        return True

    @staticmethod
    def validate_cron_expression(expression: str) -> bool:
        """
        Validate if a cron expression is valid

        Args:
            expression: Cron expression string

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Test with a recent datetime to see if it's valid
            croniter.croniter(expression, datetime.utcnow())
            return True
        except:
            return False

    @staticmethod
    def get_upcoming_recurring_instances(
        session: Session,
        parent_task_id: int,
        limit: int = 10
    ) -> List[Task]:
        """
        Get upcoming instances of a recurring task (excluding parent)

        Args:
            session: Database session
            parent_task_id: Parent task ID
            limit: Maximum number of instances to return

        Returns:
            List[Task]: List of upcoming task instances
        """
        from sqlmodel import select

        # Get all tasks derived from parent (including incomplete ones)
        stmt = select(Task).where(
            Task.parent_task_id == parent_task_id,
            Task.completed == False
        ).order_by(Task.due_date).limit(limit)

        return session.exec(stmt).all()


# Singleton instance
recurring_task_service = RecurringTaskService()
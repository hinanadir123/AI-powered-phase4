"""
Reminder Service for handling task reminders
Phase 5 - Advanced Features
"""

from datetime import datetime, timedelta
from typing import List, Optional
from models import Task
from sqlmodel import Session, select


class ReminderService:
    """Service for managing task reminders"""

    @staticmethod
    def should_send_reminder(task: Task) -> bool:
        """
        Check if a reminder should be sent for a task

        Args:
            task: Task to check

        Returns:
            True if reminder should be sent, False otherwise
        """
        if not task.reminder_time or task.completed:
            return False

        now = datetime.utcnow()
        return now >= task.reminder_time

    @staticmethod
    def get_tasks_needing_reminders(session: Session) -> List[Task]:
        """
        Get all tasks that need reminders sent

        Args:
            session: Database session

        Returns:
            List of tasks needing reminders
        """
        now = datetime.utcnow()

        query = select(Task).where(
            Task.reminder_time <= now,
            Task.completed == False,
            Task.reminder_time.isnot(None)
        )

        return list(session.exec(query).all())

    @staticmethod
    def calculate_reminder_time(
        due_date: datetime,
        minutes_before: int = 60
    ) -> datetime:
        """
        Calculate reminder time based on due date

        Args:
            due_date: Task due date
            minutes_before: Minutes before due date to send reminder

        Returns:
            Calculated reminder time
        """
        return due_date - timedelta(minutes=minutes_before)

    @staticmethod
    def send_reminder(task: Task) -> bool:
        """
        Send a reminder for a task (placeholder for actual notification)

        Args:
            task: Task to send reminder for

        Returns:
            True if reminder was sent successfully
        """
        # TODO: Integrate with Dapr Pub/Sub in Step 3
        # For now, just log the reminder
        print(f"[REMINDER] Task '{task.title}' is due soon!")
        print(f"  - Due Date: {task.due_date}")
        print(f"  - Priority: {task.priority}")

        return True

    @staticmethod
    def process_reminders(session: Session) -> int:
        """
        Process all pending reminders

        Args:
            session: Database session

        Returns:
            Number of reminders sent
        """
        tasks = ReminderService.get_tasks_needing_reminders(session)
        count = 0

        for task in tasks:
            if ReminderService.send_reminder(task):
                # Clear reminder_time after sending to avoid duplicate reminders
                task.reminder_time = None
                session.add(task)
                count += 1

        session.commit()
        return count

# Task: T5.3.4 - Dapr Jobs API Integration for Scheduling
# Spec Reference: phase5-spec.md Section 3.2.2 (Due Dates & Reminders)
# Constitution: constitution.md v5.0 Section 4.2 (Event Flow)
#
# This module provides integration with Dapr Jobs API for:
# - Scheduling reminder notifications
# - Creating recurring task instances
# - Managing scheduled jobs lifecycle
#
# Version: 1.0
# Date: 2026-02-15

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DaprJobsClient:
    """
    Client for interacting with Dapr Jobs API.

    Provides methods to schedule, retrieve, update, and delete jobs.
    """

    def __init__(self, dapr_http_port: int = 3500):
        """
        Initialize Dapr Jobs API client.

        Args:
            dapr_http_port: Dapr sidecar HTTP port (default: 3500)
        """
        self.base_url = f"http://localhost:{dapr_http_port}/v1.0-alpha1/jobs"
        self.timeout = 10

    def schedule_job(
        self,
        job_name: str,
        schedule_time: datetime,
        data: Dict[str, Any],
        repeats: int = 0,
        ttl: Optional[str] = None
    ) -> bool:
        """
        Schedule a new job via Dapr Jobs API.

        Args:
            job_name: Unique job identifier
            schedule_time: When to execute the job
            data: Job payload data
            repeats: Number of times to repeat (0 = one-time)
            ttl: Time-to-live for the job (e.g., "1h", "1d")

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/{job_name}"

        payload = {
            "schedule": schedule_time.isoformat() + "Z",
            "repeats": repeats,
            "data": data
        }

        if ttl:
            payload["ttl"] = ttl

        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )

            if response.status_code in [200, 201, 204]:
                logger.info(f"✅ Scheduled job '{job_name}' at {schedule_time}")
                return True
            else:
                logger.error(f"❌ Failed to schedule job: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error scheduling job '{job_name}': {str(e)}")
            return False

    def get_job(self, job_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve job details.

        Args:
            job_name: Job identifier

        Returns:
            Job details dictionary or None if not found
        """
        url = f"{self.base_url}/{job_name}"

        try:
            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Job '{job_name}' not found")
                return None
            else:
                logger.error(f"❌ Failed to get job: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error getting job '{job_name}': {str(e)}")
            return None

    def delete_job(self, job_name: str) -> bool:
        """
        Delete a scheduled job.

        Args:
            job_name: Job identifier

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/{job_name}"

        try:
            response = requests.delete(url, timeout=self.timeout)

            if response.status_code in [200, 204]:
                logger.info(f"✅ Deleted job '{job_name}'")
                return True
            elif response.status_code == 404:
                logger.warning(f"Job '{job_name}' not found")
                return False
            else:
                logger.error(f"❌ Failed to delete job: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error deleting job '{job_name}': {str(e)}")
            return False


class ReminderScheduler:
    """
    High-level scheduler for task reminders using Dapr Jobs API.
    """

    def __init__(self, jobs_client: Optional[DaprJobsClient] = None):
        """
        Initialize reminder scheduler.

        Args:
            jobs_client: DaprJobsClient instance (creates new if None)
        """
        self.jobs_client = jobs_client or DaprJobsClient()

    def schedule_reminder(
        self,
        task_id: str,
        task_title: str,
        due_date: datetime,
        time_before: str,
        channels: List[str],
        user_id: str
    ) -> bool:
        """
        Schedule a reminder for a task.

        Args:
            task_id: Task identifier
            task_title: Task title
            due_date: Task due date
            time_before: Time before due date (e.g., "1h", "1d")
            channels: Notification channels (email, push, etc.)
            user_id: User identifier

        Returns:
            True if successful, False otherwise
        """
        # Parse time_before to calculate reminder time
        reminder_time = self._calculate_reminder_time(due_date, time_before)

        if reminder_time <= datetime.utcnow():
            logger.warning(f"Reminder time is in the past for task {task_id}")
            return False

        job_name = f"reminder-{task_id}"
        job_data = {
            "type": "reminder",
            "task_id": task_id,
            "task_title": task_title,
            "due_date": due_date.isoformat(),
            "channels": channels,
            "user_id": user_id
        }

        return self.jobs_client.schedule_job(
            job_name=job_name,
            schedule_time=reminder_time,
            data=job_data,
            repeats=0,
            ttl="7d"  # Job expires after 7 days
        )

    def cancel_reminder(self, task_id: str) -> bool:
        """
        Cancel a scheduled reminder.

        Args:
            task_id: Task identifier

        Returns:
            True if successful, False otherwise
        """
        job_name = f"reminder-{task_id}"
        return self.jobs_client.delete_job(job_name)

    def _calculate_reminder_time(self, due_date: datetime, time_before: str) -> datetime:
        """
        Calculate when reminder should trigger.

        Args:
            due_date: Task due date
            time_before: Time before due date (e.g., "15m", "1h", "1d")

        Returns:
            Reminder trigger time
        """
        unit = time_before[-1]
        value = int(time_before[:-1])

        multipliers = {
            'm': 60,           # minutes
            'h': 3600,         # hours
            'd': 86400,        # days
            'w': 604800        # weeks
        }

        seconds = value * multipliers.get(unit, 3600)
        return due_date - timedelta(seconds=seconds)


class RecurringTaskScheduler:
    """
    High-level scheduler for recurring tasks using Dapr Jobs API.
    """

    def __init__(self, jobs_client: Optional[DaprJobsClient] = None):
        """
        Initialize recurring task scheduler.

        Args:
            jobs_client: DaprJobsClient instance (creates new if None)
        """
        self.jobs_client = jobs_client or DaprJobsClient()

    def schedule_next_occurrence(
        self,
        parent_task_id: str,
        task_data: Dict[str, Any],
        recurrence_config: Dict[str, Any]
    ) -> bool:
        """
        Schedule the next occurrence of a recurring task.

        Args:
            parent_task_id: Parent task identifier
            task_data: Task data to replicate
            recurrence_config: Recurrence configuration

        Returns:
            True if successful, False otherwise
        """
        next_time = self._calculate_next_occurrence(recurrence_config)

        if not next_time:
            logger.info(f"Recurrence ended for task {parent_task_id}")
            return False

        job_name = f"recurring-{parent_task_id}"
        job_data = {
            "type": "recurring_task",
            "parent_task_id": parent_task_id,
            "task_data": task_data,
            "recurrence_config": recurrence_config
        }

        return self.jobs_client.schedule_job(
            job_name=job_name,
            schedule_time=next_time,
            data=job_data,
            repeats=0
        )

    def cancel_recurrence(self, parent_task_id: str) -> bool:
        """
        Cancel recurring task schedule.

        Args:
            parent_task_id: Parent task identifier

        Returns:
            True if successful, False otherwise
        """
        job_name = f"recurring-{parent_task_id}"
        return self.jobs_client.delete_job(job_name)

    def _calculate_next_occurrence(self, recurrence_config: Dict[str, Any]) -> Optional[datetime]:
        """
        Calculate next occurrence time based on recurrence configuration.

        Args:
            recurrence_config: Recurrence configuration

        Returns:
            Next occurrence time or None if recurrence ended
        """
        if not recurrence_config.get("enabled"):
            return None

        interval = recurrence_config.get("interval")
        frequency = recurrence_config.get("frequency", 1)
        end_date = recurrence_config.get("end_date")

        now = datetime.utcnow()

        # Calculate next time based on interval
        if interval == "daily":
            next_time = now + timedelta(days=frequency)
        elif interval == "weekly":
            next_time = now + timedelta(weeks=frequency)
        elif interval == "monthly":
            next_time = now + timedelta(days=30 * frequency)
        else:
            logger.warning(f"Unsupported interval: {interval}")
            return None

        # Check if end_date has passed
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            if next_time > end_dt:
                return None

        return next_time


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize schedulers
    reminder_scheduler = ReminderScheduler()
    recurring_scheduler = RecurringTaskScheduler()

    # Example: Schedule a reminder
    due_date = datetime.utcnow() + timedelta(hours=2)
    reminder_scheduler.schedule_reminder(
        task_id="task-123",
        task_title="Complete Phase 5",
        due_date=due_date,
        time_before="1h",
        channels=["email", "push"],
        user_id="user-456"
    )

    # Example: Schedule recurring task
    task_data = {
        "title": "Weekly standup",
        "description": "Team standup meeting",
        "priority": "medium"
    }
    recurrence_config = {
        "enabled": True,
        "interval": "weekly",
        "frequency": 1,
        "days": ["monday"],
        "end_date": None
    }
    recurring_scheduler.schedule_next_occurrence(
        parent_task_id="task-456",
        task_data=task_data,
        recurrence_config=recurrence_config
    )

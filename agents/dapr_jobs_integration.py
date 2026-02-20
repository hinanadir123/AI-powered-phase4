"""
Dapr Jobs Integration for Scheduling Reminders
Task: Integrate Dapr Jobs API for scheduling reminders
Spec Reference: phase5-spec.md Section 4.4 (Job Scheduling)
Constitution: constitution.md v5.0
"""
import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class JobStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    COMPLETED = "completed"
    SCHEDULED = "scheduled"


class DaprJobsScheduler:
    """
    Dapr Jobs API Implementation for scheduling task reminders
    Uses Dapr HTTP API to schedule jobs via the Jobs API component
    """

    def __init__(self):
        self.dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
        self.dapr_jobs_url = f"http://localhost:{self.dapr_port}/v1.0/jobs"
        self.jobs_store_name = os.getenv("DAPR_JOBS_STORE", "jobs-scheduler")
        self.enabled = os.getenv("DAPR_JOBS_ENABLED", "true").lower() == "true"

    def schedule_reminder_job(
        self,
        task_id: int,
        user_id: str,
        reminder_time: datetime,
        title: str,
        priority: str = "medium",
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Schedule a reminder job using Dapr Jobs API

        Args:
            task_id: ID of the task
            user_id: User ID
            reminder_time: When to trigger the reminder
            title: Task title
            priority: Task priority
            description: Task description (optional)
            metadata: Additional metadata for the job

        Returns:
            bool: True if scheduled successfully
        """
        if not self.enabled:
            print(f"[JOBS DISABLED] Would schedule reminder for task {task_id} at {reminder_time}")
            return True

        try:
            # Prepare job payload
            job_data = {
                "job": {
                    "id": f"reminder-{task_id}-{reminder_time.timestamp()}",
                    "schedule": reminder_time.isoformat(),
                    "payload": {
                        "task_id": task_id,
                        "user_id": user_id,
                        "title": title,
                        "priority": priority,
                        "description": description,
                        "triggered_time": datetime.utcnow().isoformat()
                    },
                    "callback": {  # This would be the target service to call when job executes
                        "method": "POST",
                        "url": "http://reminder-worker/api/trigger-reminder",  # Example URL
                        "headers": {
                            "Content-Type": "application/json"
                        }
                    }
                }
            }

            # Make request to schedule job via Dapr API
            # Note: Dapr Jobs API might work differently based on actual implementation
            # This is following the pattern based on Dapr documentation
            url = f"{self.dapr_jobs_url}/{self.jobs_store_name}/jobs"

            response = requests.post(
                url,
                json=job_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code in [200, 201, 202]:
                print(f"[JOB SCHEDULED] Reminder job for task {task_id} scheduled at {reminder_time}")
                return True
            else:
                print(f"[JOB FAILED] Scheduling reminder job: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"[JOB ERROR] Failed to schedule reminder job for task {task_id}: {e}")
            return False

    def schedule_recurring_task_job(
        self,
        parent_task_id: int,
        user_id: str,
        start_time: datetime,
        cron_expression: str,
        title: str,
        max_occurrences: Optional[int] = 10,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Schedule a recurring task job using Dapr Jobs API

        Args:
            parent_task_id: ID of the parent recurring task
            user_id: User ID
            start_time: When the recurrence should begin
            cron_expression: Schedule using cron expression
            title: Task title for reference
            max_occurrences: Maximum number of instances to create (None for unlimited)
            metadata: Additional metadata for the job

        Returns:
            bool: True if scheduled successfully
        """
        if not self.enabled:
            print(f"[JOBS DISABLED] Would schedule recurring job for parent task {parent_task_id}")
            return True

        try:
            job_data = {
                "job": {
                    "id": f"recurring-{parent_task_id}-{start_time.timestamp()}",
                    "cron": cron_expression,  # Use cron if supported
                    "payload": {
                        "parent_task_id": parent_task_id,
                        "user_id": user_id,
                        "title": title,
                        "max_occurrences": max_occurrences,
                        "created_at": datetime.utcnow().isoformat()
                    },
                    "callback": {
                        "method": "POST",
                        "url": "http://backend/api/{user_id}/tasks/{parent_task_id}/create-next-instance",
                        "headers": {
                            "Content-Type": "application/json"
                        }
                    }
                }
            }

            url = f"{self.dapr_jobs_url}/{self.jobs_store_name}/jobs"

            response = requests.post(
                url,
                json=job_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code in [200, 201, 202]:
                print(f"[JOB SCHEDULED] Recurring job for parent task {parent_task_id} set with cron {cron_expression}")
                return True
            else:
                print(f"[JOB FAILED] Scheduling recurring job: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"[JOB ERROR] Failed to schedule recurring job for parent task {parent_task_id}: {e}")
            return False

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a scheduled job

        Args:
            job_id: ID of the job to check

        Returns:
            Job status information or None if failed
        """
        if not self.enabled:
            print(f"[JOBS DISABLED] Job status check for {job_id}")
            return {
                "job_id": job_id,
                "status": "mocked",
                "last_run": datetime.utcnow().isoformat()
            }

        try:
            url = f"{self.dapr_jobs_url}/{self.jobs_store_name}/jobs/{job_id}"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"[JOB STATUS ERROR] {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"[JOB STATUS ERROR] Failed to get job status for {job_id}: {e}")
            return None

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a scheduled job

        Args:
            job_id: ID of the job to cancel

        Returns:
            bool: True if cancelled successfully
        """
        if not self.enabled:
            print(f"[JOBS DISABLED] Would cancel job {job_id}")
            return True

        try:
            url = f"{self.dapr_jobs_url}/{self.jobs_store_name}/jobs/{job_id}"

            response = requests.delete(url, timeout=10)

            if response.status_code == 204:  # No Content = Success
                print(f"[JOB CANCELLED] Job {job_id} has been cancelled")
                return True
            else:
                print(f"[JOB CANCEL FAILED] {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"[JOB CANCEL ERROR] Failed to cancel job {job_id}: {e}")
            return False


class ReminderJobScheduler:
    """
    Higher-level scheduler for task reminders that uses Dapr Jobs
    """
    def __init__(self):
        self.dapr_scheduler = DaprJobsScheduler()

    def schedule_task_reminder(
        self,
        task_id: int,
        user_id: str,
        reminder_time: datetime,
        task_title: str = "",
        task_priority: str = "medium",
        task_description: str = ""
    ) -> bool:
        """
        Schedule a reminder for a specific task
        """
        return self.dapr_scheduler.schedule_reminder_job(
            task_id=task_id,
            user_id=user_id,
            reminder_time=reminder_time,
            title=task_title,
            priority=task_priority,
            description=task_description
        )

    def schedule_recurring_task_instance_creation(
        self,
        parent_task_id: int,
        user_id: str,
        cron_expression: str,
        title: str,
        max_instances: Optional[int] = 10
    ) -> bool:
        """
        Schedule creation of recurring task instances
        """
        from datetime import datetime
        return self.dapr_scheduler.schedule_recurring_task_job(
            parent_task_id=parent_task_id,
            user_id=user_id,
            start_time=datetime.utcnow(),
            cron_expression=cron_expression,
            title=title,
            max_occurrences=max_instances
        )

    def get_scheduled_reminders_stats(self) -> Dict[str, Any]:
        """
        Get statistics about scheduled reminders
        (For demo purposes - in a real implementation, this would query the jobs store)
        """
        return {
            "total_scheduled": 0,  # Placeholder
            "upcoming_24h": 0,  # Placeholder
            "successful_reminders": 0,  # Placeholder
            "failed_reminders": 0  # Placeholder
        }


# Global instance for the job scheduler
job_scheduler = ReminderJobScheduler()
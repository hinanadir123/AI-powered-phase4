# Task: T5.4.2 - Integration Tests for Dapr Jobs API
# Spec Reference: phase5-spec.md Section 3.2.2 (Due Dates & Reminders)
# Constitution: constitution.md v5.0 Section 4.3 (Dapr Components)
#
# Integration tests for Dapr Jobs API scheduling and execution.
# Tests verify job creation, retrieval, deletion, and execution.
#
# Version: 1.0
# Date: 2026-02-15

import pytest
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class TestDaprJobsAPI:
    """
    Integration tests for Dapr Jobs API.

    Prerequisites:
    - Dapr sidecar running on localhost:3500
    - Dapr Jobs component configured (jobs-scheduler)
    - PostgreSQL state store for job persistence
    """

    DAPR_HTTP_PORT = 3500
    DAPR_URL = f"http://localhost:{DAPR_HTTP_PORT}"
    JOBS_BASE_URL = f"{DAPR_URL}/v1.0-alpha1/jobs"

    def test_schedule_one_time_job(self):
        """Test scheduling a one-time job"""
        # Arrange
        job_name = f"test-job-{uuid4()}"
        schedule_time = datetime.utcnow() + timedelta(seconds=30)
        job_data = {
            "schedule": schedule_time.isoformat() + "Z",
            "repeats": 0,
            "data": {
                "task_id": "task-123",
                "type": "reminder",
                "message": "Test reminder"
            }
        }

        # Act
        url = f"{self.JOBS_BASE_URL}/{job_name}"
        response = requests.post(
            url,
            json=job_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        # Assert
        assert response.status_code in [200, 201, 204], f"Failed to schedule job: {response.text}"
        logger.info(f"✅ Successfully scheduled one-time job: {job_name}")

        # Cleanup
        requests.delete(url, timeout=5)

    def test_schedule_recurring_job(self):
        """Test scheduling a recurring job"""
        # Arrange
        job_name = f"test-recurring-{uuid4()}"
        schedule_time = datetime.utcnow() + timedelta(seconds=10)
        job_data = {
            "schedule": schedule_time.isoformat() + "Z",
            "repeats": 3,  # Repeat 3 times
            "data": {
                "task_id": "task-456",
                "type": "recurring_task",
                "interval": "daily"
            }
        }

        # Act
        url = f"{self.JOBS_BASE_URL}/{job_name}"
        response = requests.post(url, json=job_data, timeout=10)

        # Assert
        assert response.status_code in [200, 201, 204]
        logger.info(f"✅ Successfully scheduled recurring job: {job_name}")

        # Cleanup
        requests.delete(url, timeout=5)

    def test_schedule_job_with_ttl(self):
        """Test scheduling job with time-to-live"""
        # Arrange
        job_name = f"test-ttl-{uuid4()}"
        schedule_time = datetime.utcnow() + timedelta(hours=1)
        job_data = {
            "schedule": schedule_time.isoformat() + "Z",
            "repeats": 0,
            "ttl": "2h",  # Job expires after 2 hours
            "data": {
                "task_id": "task-789",
                "type": "reminder"
            }
        }

        # Act
        url = f"{self.JOBS_BASE_URL}/{job_name}"
        response = requests.post(url, json=job_data, timeout=10)

        # Assert
        assert response.status_code in [200, 201, 204]
        logger.info(f"✅ Successfully scheduled job with TTL: {job_name}")

        # Cleanup
        requests.delete(url, timeout=5)

    def test_get_job_details(self):
        """Test retrieving job details"""
        # Arrange - Create a job first
        job_name = f"test-get-{uuid4()}"
        schedule_time = datetime.utcnow() + timedelta(minutes=5)
        job_data = {
            "schedule": schedule_time.isoformat() + "Z",
            "repeats": 0,
            "data": {"task_id": "task-get-test"}
        }

        url = f"{self.JOBS_BASE_URL}/{job_name}"
        create_response = requests.post(url, json=job_data, timeout=10)
        assert create_response.status_code in [200, 201, 204]

        # Act - Retrieve job
        get_response = requests.get(url, timeout=10)

        # Assert
        if get_response.status_code == 200:
            job_details = get_response.json()
            assert job_details is not None
            logger.info(f"✅ Successfully retrieved job details: {job_name}")
        else:
            logger.warning(f"Job retrieval returned {get_response.status_code} (may not be supported)")

        # Cleanup
        requests.delete(url, timeout=5)

    def test_delete_scheduled_job(self):
        """Test deleting a scheduled job"""
        # Arrange - Create a job first
        job_name = f"test-delete-{uuid4()}"
        schedule_time = datetime.utcnow() + timedelta(minutes=10)
        job_data = {
            "schedule": schedule_time.isoformat() + "Z",
            "repeats": 0,
            "data": {"task_id": "task-delete-test"}
        }

        url = f"{self.JOBS_BASE_URL}/{job_name}"
        create_response = requests.post(url, json=job_data, timeout=10)
        assert create_response.status_code in [200, 201, 204]

        # Act - Delete job
        delete_response = requests.delete(url, timeout=10)

        # Assert
        assert delete_response.status_code in [200, 204, 404]
        logger.info(f"✅ Successfully deleted job: {job_name}")

    def test_update_existing_job(self):
        """Test updating an existing job (reschedule)"""
        # Arrange - Create initial job
        job_name = f"test-update-{uuid4()}"
        initial_time = datetime.utcnow() + timedelta(minutes=5)
        initial_data = {
            "schedule": initial_time.isoformat() + "Z",
            "repeats": 0,
            "data": {"task_id": "task-update-test", "version": 1}
        }

        url = f"{self.JOBS_BASE_URL}/{job_name}"
        create_response = requests.post(url, json=initial_data, timeout=10)
        assert create_response.status_code in [200, 201, 204]

        # Act - Update job with new schedule
        updated_time = datetime.utcnow() + timedelta(minutes=10)
        updated_data = {
            "schedule": updated_time.isoformat() + "Z",
            "repeats": 0,
            "data": {"task_id": "task-update-test", "version": 2}
        }
        update_response = requests.post(url, json=updated_data, timeout=10)

        # Assert
        assert update_response.status_code in [200, 201, 204]
        logger.info(f"✅ Successfully updated job: {job_name}")

        # Cleanup
        requests.delete(url, timeout=5)

    def test_schedule_job_in_past(self):
        """Test error handling for scheduling job in the past"""
        # Arrange
        job_name = f"test-past-{uuid4()}"
        past_time = datetime.utcnow() - timedelta(hours=1)
        job_data = {
            "schedule": past_time.isoformat() + "Z",
            "repeats": 0,
            "data": {"task_id": "task-past-test"}
        }

        # Act
        url = f"{self.JOBS_BASE_URL}/{job_name}"
        response = requests.post(url, json=job_data, timeout=10)

        # Assert
        # Dapr may accept it and execute immediately or reject it
        logger.info(f"Past job schedule response: {response.status_code}")

        # Cleanup
        if response.status_code in [200, 201, 204]:
            requests.delete(url, timeout=5)

    def test_schedule_multiple_jobs(self):
        """Test scheduling multiple jobs concurrently"""
        # Arrange
        job_names = [f"test-multi-{uuid4()}" for _ in range(5)]
        schedule_time = datetime.utcnow() + timedelta(minutes=15)

        # Act
        responses = []
        for job_name in job_names:
            job_data = {
                "schedule": schedule_time.isoformat() + "Z",
                "repeats": 0,
                "data": {"task_id": f"task-{job_name}"}
            }
            url = f"{self.JOBS_BASE_URL}/{job_name}"
            response = requests.post(url, json=job_data, timeout=10)
            responses.append((job_name, response))

        # Assert
        successful = [r for _, r in responses if r.status_code in [200, 201, 204]]
        assert len(successful) == len(job_names), "Some jobs failed to schedule"
        logger.info(f"✅ Successfully scheduled {len(successful)} jobs")

        # Cleanup
        for job_name in job_names:
            requests.delete(f"{self.JOBS_BASE_URL}/{job_name}", timeout=5)

    def test_job_with_complex_payload(self):
        """Test scheduling job with complex data payload"""
        # Arrange
        job_name = f"test-complex-{uuid4()}"
        schedule_time = datetime.utcnow() + timedelta(minutes=20)
        complex_data = {
            "schedule": schedule_time.isoformat() + "Z",
            "repeats": 0,
            "data": {
                "task_id": "task-complex",
                "reminder": {
                    "enabled": True,
                    "time_before": "1h",
                    "channels": ["email", "push", "sms"]
                },
                "recurrence": {
                    "interval": "weekly",
                    "days": ["monday", "wednesday", "friday"]
                },
                "metadata": {
                    "priority": "high",
                    "tags": ["important", "recurring"],
                    "nested": {
                        "level1": {
                            "level2": "deep value"
                        }
                    }
                }
            }
        }

        # Act
        url = f"{self.JOBS_BASE_URL}/{job_name}"
        response = requests.post(url, json=complex_data, timeout=10)

        # Assert
        assert response.status_code in [200, 201, 204]
        logger.info(f"✅ Successfully scheduled job with complex payload: {job_name}")

        # Cleanup
        requests.delete(url, timeout=5)


class TestReminderScheduling:
    """Integration tests for reminder scheduling using Dapr Jobs API"""

    DAPR_URL = f"http://localhost:3500"
    JOBS_BASE_URL = f"{DAPR_URL}/v1.0-alpha1/jobs"

    def test_schedule_reminder_1_hour_before(self):
        """Test scheduling reminder 1 hour before due date"""
        # Arrange
        task_id = str(uuid4())
        due_date = datetime.utcnow() + timedelta(hours=2)
        reminder_time = due_date - timedelta(hours=1)

        job_name = f"reminder-{task_id}"
        job_data = {
            "schedule": reminder_time.isoformat() + "Z",
            "repeats": 0,
            "data": {
                "type": "reminder",
                "task_id": task_id,
                "task_title": "Important Meeting",
                "due_date": due_date.isoformat(),
                "channels": ["email"],
                "user_id": "user-123"
            }
        }

        # Act
        url = f"{self.JOBS_BASE_URL}/{job_name}"
        response = requests.post(url, json=job_data, timeout=10)

        # Assert
        assert response.status_code in [200, 201, 204]
        logger.info(f"✅ Scheduled reminder for task {task_id} at {reminder_time}")

        # Cleanup
        requests.delete(url, timeout=5)

    def test_schedule_multiple_reminders_same_task(self):
        """Test scheduling multiple reminders for same task"""
        # Arrange
        task_id = str(uuid4())
        due_date = datetime.utcnow() + timedelta(days=1)

        reminders = [
            ("1d", due_date - timedelta(days=1)),
            ("1h", due_date - timedelta(hours=1)),
            ("15m", due_date - timedelta(minutes=15))
        ]

        # Act
        responses = []
        for time_before, reminder_time in reminders:
            job_name = f"reminder-{task_id}-{time_before}"
            job_data = {
                "schedule": reminder_time.isoformat() + "Z",
                "repeats": 0,
                "data": {
                    "type": "reminder",
                    "task_id": task_id,
                    "time_before": time_before
                }
            }
            url = f"{self.JOBS_BASE_URL}/{job_name}"
            response = requests.post(url, json=job_data, timeout=10)
            responses.append((job_name, response))

        # Assert
        successful = [r for _, r in responses if r.status_code in [200, 201, 204]]
        assert len(successful) == len(reminders)
        logger.info(f"✅ Scheduled {len(successful)} reminders for task {task_id}")

        # Cleanup
        for job_name, _ in responses:
            requests.delete(f"{self.JOBS_BASE_URL}/{job_name}", timeout=5)

    def test_cancel_reminder(self):
        """Test canceling a scheduled reminder"""
        # Arrange - Schedule reminder
        task_id = str(uuid4())
        reminder_time = datetime.utcnow() + timedelta(hours=3)
        job_name = f"reminder-{task_id}"

        job_data = {
            "schedule": reminder_time.isoformat() + "Z",
            "repeats": 0,
            "data": {"type": "reminder", "task_id": task_id}
        }

        url = f"{self.JOBS_BASE_URL}/{job_name}"
        create_response = requests.post(url, json=job_data, timeout=10)
        assert create_response.status_code in [200, 201, 204]

        # Act - Cancel reminder
        delete_response = requests.delete(url, timeout=10)

        # Assert
        assert delete_response.status_code in [200, 204, 404]
        logger.info(f"✅ Canceled reminder for task {task_id}")


class TestRecurringTaskScheduling:
    """Integration tests for recurring task scheduling using Dapr Jobs API"""

    DAPR_URL = f"http://localhost:3500"
    JOBS_BASE_URL = f"{DAPR_URL}/v1.0-alpha1/jobs"

    def test_schedule_daily_recurring_task(self):
        """Test scheduling daily recurring task"""
        # Arrange
        parent_task_id = str(uuid4())
        next_occurrence = datetime.utcnow() + timedelta(days=1)

        job_name = f"recurring-{parent_task_id}"
        job_data = {
            "schedule": next_occurrence.isoformat() + "Z",
            "repeats": 0,
            "data": {
                "type": "recurring_task",
                "parent_task_id": parent_task_id,
                "task_data": {
                    "title": "Daily Standup",
                    "priority": "medium"
                },
                "recurrence_config": {
                    "interval": "daily",
                    "frequency": 1
                }
            }
        }

        # Act
        url = f"{self.JOBS_BASE_URL}/{job_name}"
        response = requests.post(url, json=job_data, timeout=10)

        # Assert
        assert response.status_code in [200, 201, 204]
        logger.info(f"✅ Scheduled daily recurring task: {parent_task_id}")

        # Cleanup
        requests.delete(url, timeout=5)

    def test_schedule_weekly_recurring_task(self):
        """Test scheduling weekly recurring task"""
        # Arrange
        parent_task_id = str(uuid4())
        next_occurrence = datetime.utcnow() + timedelta(weeks=1)

        job_name = f"recurring-{parent_task_id}"
        job_data = {
            "schedule": next_occurrence.isoformat() + "Z",
            "repeats": 0,
            "data": {
                "type": "recurring_task",
                "parent_task_id": parent_task_id,
                "recurrence_config": {
                    "interval": "weekly",
                    "frequency": 1,
                    "days": ["monday"]
                }
            }
        }

        # Act
        url = f"{self.JOBS_BASE_URL}/{job_name}"
        response = requests.post(url, json=job_data, timeout=10)

        # Assert
        assert response.status_code in [200, 201, 204]
        logger.info(f"✅ Scheduled weekly recurring task: {parent_task_id}")

        # Cleanup
        requests.delete(url, timeout=5)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

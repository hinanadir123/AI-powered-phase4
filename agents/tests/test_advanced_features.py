# Task: T5.3.1, T5.3.2, T5.3.3, T5.3.4, T5.3.5 - Unit Tests for Advanced Features
# Spec Reference: phase5-spec.md Section 3.2 (Advanced Features)
# Constitution: constitution.md v5.0 Section 10.1 (Code Validation)
#
# Comprehensive unit tests for:
# - Task model with recurrence, due dates, reminders
# - Kafka event publisher
# - Reminder worker
# - Dapr Jobs API integration
# - API endpoints
#
# Version: 1.0
# Date: 2026-02-15

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import json

# Import modules to test
import sys
sys.path.insert(0, '../backend')

from models_advanced_features import (
    TaskAdvanced, RecurrenceConfig, ReminderConfig,
    TaskCreate, TaskUpdate, TaskResponse
)
from task_event_publisher import TaskEventPublisher
from reminder_worker import ReminderWorker
from dapr_jobs_integration import (
    DaprJobsClient, ReminderScheduler, RecurringTaskScheduler
)


class TestTaskAdvancedModel:
    """Test cases for TaskAdvanced model"""

    def test_task_creation_with_basic_fields(self):
        """Test creating a task with basic fields"""
        task = TaskAdvanced(
            title="Test Task",
            description="Test Description",
            user_id="user-123"
        )

        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.status == "pending"
        assert task.priority == "medium"
        assert task.tags == []
        assert task.due_date is None
        assert task.recurrence is None
        assert task.reminder is None

    def test_task_creation_with_advanced_fields(self):
        """Test creating a task with advanced fields"""
        due_date = datetime.utcnow() + timedelta(days=1)
        recurrence = {
            "enabled": True,
            "interval": "weekly",
            "frequency": 1,
            "days": ["monday", "wednesday"]
        }
        reminder = {
            "enabled": True,
            "time_before": "1h",
            "channels": ["email", "push"]
        }

        task = TaskAdvanced(
            title="Advanced Task",
            user_id="user-123",
            priority="high",
            tags=["work", "urgent"],
            due_date=due_date,
            recurrence=recurrence,
            reminder=reminder
        )

        assert task.priority == "high"
        assert task.tags == ["work", "urgent"]
        assert task.due_date == due_date
        assert task.recurrence == recurrence
        assert task.reminder == reminder

    def test_recurrence_config_validation(self):
        """Test RecurrenceConfig validation"""
        config = RecurrenceConfig(
            enabled=True,
            interval="weekly",
            frequency=2,
            days=["monday", "friday"]
        )

        assert config.enabled is True
        assert config.interval == "weekly"
        assert config.frequency == 2
        assert config.days == ["monday", "friday"]

    def test_reminder_config_validation(self):
        """Test ReminderConfig validation"""
        config = ReminderConfig(
            enabled=True,
            time_before="1h",
            channels=["email"]
        )

        assert config.enabled is True
        assert config.time_before == "1h"
        assert config.channels == ["email"]


class TestTaskEventPublisher:
    """Test cases for TaskEventPublisher"""

    @patch('task_event_publisher.requests.post')
    def test_publish_task_created_success(self, mock_post):
        """Test successful task.created event publishing"""
        mock_post.return_value.status_code = 200

        publisher = TaskEventPublisher()
        task_data = {
            "id": "task-123",
            "title": "Test Task",
            "user_id": "user-456",
            "created_at": datetime.utcnow().isoformat()
        }

        result = publisher.publish_task_created(task_data)

        assert result is True
        assert mock_post.called
        call_args = mock_post.call_args
        assert "task-events" in call_args[0][0]

    @patch('task_event_publisher.requests.post')
    def test_publish_task_updated_success(self, mock_post):
        """Test successful task.updated event publishing"""
        mock_post.return_value.status_code = 200

        publisher = TaskEventPublisher()
        task_data = {
            "id": "task-123",
            "title": "Updated Task",
            "status": "completed",
            "user_id": "user-456"
        }
        changes = {"status": {"old": "pending", "new": "completed"}}

        result = publisher.publish_task_updated(task_data, changes)

        assert result is True
        assert mock_post.called

    @patch('task_event_publisher.requests.post')
    def test_publish_task_completed_success(self, mock_post):
        """Test successful task.completed event publishing"""
        mock_post.return_value.status_code = 200

        publisher = TaskEventPublisher()
        task_data = {
            "id": "task-123",
            "title": "Completed Task",
            "user_id": "user-456",
            "recurrence": {"enabled": True, "interval": "weekly"}
        }

        result = publisher.publish_task_completed(task_data)

        assert result is True
        assert mock_post.called

    @patch('task_event_publisher.requests.post')
    def test_publish_event_failure(self, mock_post):
        """Test event publishing failure handling"""
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"

        publisher = TaskEventPublisher()
        task_data = {
            "id": "task-123",
            "title": "Test Task",
            "user_id": "user-456",
            "created_at": datetime.utcnow().isoformat()
        }

        result = publisher.publish_task_created(task_data)

        assert result is False


class TestReminderWorker:
    """Test cases for ReminderWorker"""

    def test_parse_time_before_minutes(self):
        """Test parsing time_before in minutes"""
        worker = ReminderWorker()
        seconds = worker.parse_time_before("15m")
        assert seconds == 900  # 15 * 60

    def test_parse_time_before_hours(self):
        """Test parsing time_before in hours"""
        worker = ReminderWorker()
        seconds = worker.parse_time_before("2h")
        assert seconds == 7200  # 2 * 3600

    def test_parse_time_before_days(self):
        """Test parsing time_before in days"""
        worker = ReminderWorker()
        seconds = worker.parse_time_before("1d")
        assert seconds == 86400  # 1 * 86400

    def test_calculate_reminder_time(self):
        """Test calculating reminder trigger time"""
        worker = ReminderWorker()
        due_date = (datetime.utcnow() + timedelta(hours=2)).isoformat() + "Z"
        reminder_time = worker.calculate_reminder_time(due_date, "1h")

        # Reminder should be 1 hour before due date
        expected_time = datetime.utcnow() + timedelta(hours=1)
        assert abs((reminder_time - expected_time).total_seconds()) < 60

    @patch('reminder_worker.requests.post')
    def test_schedule_reminder_job_success(self, mock_post):
        """Test successful reminder job scheduling"""
        mock_post.return_value.status_code = 200

        worker = ReminderWorker()
        reminder_time = datetime.utcnow() + timedelta(hours=1)
        task_data = {
            "title": "Test Task",
            "due_date": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            "reminder": {"channels": ["email"]},
            "user_id": "user-123"
        }

        result = worker.schedule_reminder_job("task-123", reminder_time, task_data)

        assert result is True
        assert mock_post.called


class TestDaprJobsClient:
    """Test cases for DaprJobsClient"""

    @patch('dapr_jobs_integration.requests.post')
    def test_schedule_job_success(self, mock_post):
        """Test successful job scheduling"""
        mock_post.return_value.status_code = 200

        client = DaprJobsClient()
        schedule_time = datetime.utcnow() + timedelta(hours=1)
        data = {"task_id": "task-123", "type": "reminder"}

        result = client.schedule_job("test-job", schedule_time, data)

        assert result is True
        assert mock_post.called

    @patch('dapr_jobs_integration.requests.get')
    def test_get_job_success(self, mock_get):
        """Test successful job retrieval"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "name": "test-job",
            "schedule": "2026-02-15T10:00:00Z"
        }

        client = DaprJobsClient()
        job = client.get_job("test-job")

        assert job is not None
        assert job["name"] == "test-job"

    @patch('dapr_jobs_integration.requests.delete')
    def test_delete_job_success(self, mock_delete):
        """Test successful job deletion"""
        mock_delete.return_value.status_code = 200

        client = DaprJobsClient()
        result = client.delete_job("test-job")

        assert result is True
        assert mock_delete.called


class TestReminderScheduler:
    """Test cases for ReminderScheduler"""

    @patch('dapr_jobs_integration.DaprJobsClient.schedule_job')
    def test_schedule_reminder_success(self, mock_schedule):
        """Test successful reminder scheduling"""
        mock_schedule.return_value = True

        scheduler = ReminderScheduler()
        due_date = datetime.utcnow() + timedelta(hours=2)

        result = scheduler.schedule_reminder(
            task_id="task-123",
            task_title="Test Task",
            due_date=due_date,
            time_before="1h",
            channels=["email"],
            user_id="user-456"
        )

        assert result is True
        assert mock_schedule.called

    @patch('dapr_jobs_integration.DaprJobsClient.delete_job')
    def test_cancel_reminder_success(self, mock_delete):
        """Test successful reminder cancellation"""
        mock_delete.return_value = True

        scheduler = ReminderScheduler()
        result = scheduler.cancel_reminder("task-123")

        assert result is True
        assert mock_delete.called


class TestRecurringTaskScheduler:
    """Test cases for RecurringTaskScheduler"""

    @patch('dapr_jobs_integration.DaprJobsClient.schedule_job')
    def test_schedule_next_occurrence_daily(self, mock_schedule):
        """Test scheduling next occurrence for daily recurrence"""
        mock_schedule.return_value = True

        scheduler = RecurringTaskScheduler()
        task_data = {"title": "Daily Task"}
        recurrence_config = {
            "enabled": True,
            "interval": "daily",
            "frequency": 1
        }

        result = scheduler.schedule_next_occurrence(
            "task-123",
            task_data,
            recurrence_config
        )

        assert result is True
        assert mock_schedule.called

    @patch('dapr_jobs_integration.DaprJobsClient.schedule_job')
    def test_schedule_next_occurrence_weekly(self, mock_schedule):
        """Test scheduling next occurrence for weekly recurrence"""
        mock_schedule.return_value = True

        scheduler = RecurringTaskScheduler()
        task_data = {"title": "Weekly Task"}
        recurrence_config = {
            "enabled": True,
            "interval": "weekly",
            "frequency": 1,
            "days": ["monday"]
        }

        result = scheduler.schedule_next_occurrence(
            "task-123",
            task_data,
            recurrence_config
        )

        assert result is True
        assert mock_schedule.called

    def test_schedule_next_occurrence_ended(self):
        """Test that recurrence doesn't schedule if end_date passed"""
        scheduler = RecurringTaskScheduler()
        task_data = {"title": "Ended Task"}
        recurrence_config = {
            "enabled": True,
            "interval": "daily",
            "frequency": 1,
            "end_date": (datetime.utcnow() - timedelta(days=1)).isoformat()
        }

        result = scheduler.schedule_next_occurrence(
            "task-123",
            task_data,
            recurrence_config
        )

        assert result is False


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

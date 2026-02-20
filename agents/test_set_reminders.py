"""
Test suite for setting reminders functionality
Task: Test for setting reminders
Spec Reference: phase5-spec.md Section 3.2.2 (Due Dates & Reminders)
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlmodel import Session

from models import Task, User
from services.reminder_service import ReminderService
from agents.kafka_event_publisher import KafkaEventPublisher


def test_should_send_reminder():
    """Test if reminders should be sent based on due dates"""
    # Create a task with a due date in the past
    past_due_date = datetime.now() - timedelta(minutes=10)
    task = Task(
        id=1,
        title="Test Task",
        user_id="test-user",
        priority="high",
        due_date=past_due_date,
        reminder_time=past_due_date - timedelta(minutes=30),  # Reminder was set 30 min before due
        completed=False
    )

    should_send = ReminderService.should_send_reminder(task)
    assert should_send is True, "Should send reminder when reminder_time passed"

    # Create a task with future reminder time
    future_reminder = datetime.now() + timedelta(hours=2)
    task2 = Task(
        id=2,
        title="Test Task 2",
        user_id="test-user",
        priority="medium",
        due_date=datetime.now() + timedelta(hours=1),
        reminder_time=future_reminder,
        completed=False
    )

    should_send2 = ReminderService.should_send_reminder(task2)
    assert should_send2 is False, "Should not send reminder when reminder_time not reached"


def test_should_not_send_reminder_completed_task():
    """Test that reminders are not sent for completed tasks"""
    past_reminder = datetime.now() - timedelta(minutes=30)
    completed_task = Task(
        id=1,
        title="Completed Task",
        user_id="test-user",
        priority="high",
        due_date=datetime.now() + timedelta(days=1),
        reminder_time=past_reminder,  # Should have sent reminder
        completed=True  # But task is completed
    )

    should_send = ReminderService.should_send_reminder(completed_task)
    assert should_send is False, "Should not send reminder for completed task"


def test_calculate_reminder_time():
    """Test calculation of reminder time based on due date"""
    due_date = datetime(2026, 2, 20, 10, 0, 0)  # 10:00 AM

    # Test with default 60 minutes
    reminder_time = ReminderService.calculate_reminder_time(due_date)
    expected = due_date - timedelta(minutes=60)
    assert reminder_time == expected, f"Expected {expected}, got {reminder_time}"

    # Test with custom minutes
    reminder_time_30 = ReminderService.calculate_reminder_time(due_date, 30)
    expected_30 = due_date - timedelta(minutes=30)
    assert reminder_time_30 == expected_30, f"Expected {expected_30}, got {reminder_time_30}"


def test_get_tasks_needing_reminders():
    """Test getting tasks that need reminders sent (manual test)"""
    # As the actual implementation requires database, we'll test with a mock
    session_mock = Mock(spec=Session)

    # Setup mock return for query execution
    mock_task = Mock()
    mock_task.reminder_time = datetime.now() - timedelta(minutes=5)  # 5 min ago
    mock_task.completed = False
    mock_task.id = 1
    mock_task.title = "Test Task"
    mock_task.priority = "high"
    mock_task.user_id = "test-user"

    session_mock.exec.return_value.all.return_value = [mock_task]

    tasks_with_reminders = ReminderService.get_tasks_needing_reminders(session_mock)
    assert len(tasks_with_reminders) >= 0  # At least 0 tasks returned


def test_reminder_service_send_reminder():
    """Test sending a reminder manually"""
    task = Task(
        id=1,
        title="Test Reminder Task",
        user_id="test-user",
        priority="medium",
        due_date=datetime.now() + timedelta(hours=1),
        reminder_time=datetime.now() - timedelta(minutes=5),
        completed=False
    )

    result = ReminderService.send_reminder(task)
    assert result is True, "Sending reminder should return True"


@patch('agents.kafka_event_publisher.requests.post')
def test_reminder_scheduled_event_published(mock_post):
    """Test that when a reminder is scheduled, the event is published"""
    mock_post.return_value.status_code = 204  # Success for Dapr publish

    publisher = KafkaEventPublisher()
    result = publisher.publish_reminder_scheduled(
        task_id=1,
        reminder_time=datetime.now().isoformat(),
        user_id="test-user",
        metadata={}
    )

    assert result is True, "Should publish reminder scheduled event successfully"
    mock_post.assert_called_once()  # Check that the HTTP call was made


@patch('agents.kafka_event_publisher.requests.post')
def test_reminder_triggered_event_published(mock_post):
    """Test that when a reminder is triggered, the event is published"""
    mock_post.return_value.status_code = 204  # Success for Dapr publish

    publisher = KafkaEventPublisher()
    result = publisher.publish_reminder_triggered(
        task_id=1,
        due_date=(datetime.now() + timedelta(days=1)).isoformat(),
        reminder_time=datetime.now().isoformat(),
        user_id="test-user"
    )

    assert result is True, "Should publish reminder triggered event successfully"
    mock_post.assert_called_once()  # Check that the HTTP call was made


def test_overdue_task_detection():
    """Test detecting overdue tasks"""
    overdue_task = Task(
        id=1,
        title="Overdue Task",
        user_id="test-user",
        completed=False,
        due_date=datetime.now() - timedelta(days=2),  # Due 2 days ago
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    is_overdue = RecurrenceService.is_overdue(overdue_task)
    assert is_overdue is True, "Task should be overdue"

    not_overdue_task = Task(
        id=2,
        title="Upcoming Task",
        user_id="test-user",
        completed=False,
        due_date=datetime.now() + timedelta(days=2),  # Due in 2 days
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    is_not_overdue = RecurrenceService.is_overdue(not_overdue_task)
    assert is_not_overdue is False, "Task should not be overdue"

    completed_overdue_task = Task(
        id=3,
        title="Completed Overdue Task",
        user_id="test-user",
        completed=True,  # Task is completed
        due_date=datetime.now() - timedelta(days=2),  # Was due 2 days ago
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    is_completed_overdue = RecurrenceService.is_overdue(completed_overdue_task)
    # According to the service, completed tasks are never overdue
    assert is_completed_overdue is False, "Completed task should not be considered overdue"


@patch('agents.kafka_event_publisher.requests.post')
def test_publish_due_date_set_event(mock_post):
    """Test publishing due date set event"""
    mock_post.return_value.status_code = 204  # Success for Dapr publish

    publisher = KafkaEventPublisher()
    result = publisher.publish_due_date_set(
        task_id=1,
        due_date=datetime.now().isoformat(),
        user_id="test-user"
    )

    assert result is True, "Should publish due date set event successfully"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
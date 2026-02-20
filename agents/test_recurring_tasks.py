"""
Test suite for recurring tasks functionality
Task: Test for creating recurring tasks
Spec Reference: phase5-spec.md Section 3.2.1 (Recurring Tasks)
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from models import Task, User, Tag, TaskTag
from agents.recurring_tasks_service import RecurringTaskService
from services.recurrence_service import RecurrenceService


# Test data
def create_test_user():
    return User(id="test-user", email="test@example.com", name="Test User")


def create_test_task(user_id):
    from datetime import datetime, timedelta
    return Task(
        id=1,
        title="Test Recurring Task",
        description="This is a recurring task test",
        user_id=user_id,
        completed=False,
        due_date=datetime.now() + timedelta(hours=1),
        recurrence_pattern='{"pattern": "daily", "frequency": 1}',
        recurrence_end_date=datetime.now() + timedelta(days=30),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        priority="medium",
    )


def test_parse_recurrence_pattern_daily():
    """Test parsing daily recurrence pattern"""
    recurrence_info = {
        'pattern': 'daily',
        'frequency': 1
    }
    cron_expr = RecurringTaskService.parse_recurrence_pattern(recurrence_info)
    assert cron_expr == "0 0 */1 * *", "Daily pattern should return correct cron expression"


def test_parse_recurrence_pattern_weekly():
    """Test parsing weekly recurrence pattern"""
    recurrence_info = {
        'pattern': 'weekly',
        'frequency': 1,
        'days': ['monday', 'wednesday', 'friday']
    }
    cron_expr = RecurringTaskService.parse_recurrence_pattern(recurrence_info)
    # Monday is 1, Wednesday is 3, Friday is 5 in our mapping
    expected = "0 0 * * 1,3,5"
    assert cron_expr == expected, f"Weekly pattern should return correct cron expression, got: {cron_expr}"


def test_parse_recurrence_pattern_monthly():
    """Test parsing monthly recurrence pattern"""
    recurrence_info = {
        'pattern': 'monthly',
        'day': 15  # 15th of every month
    }
    cron_expr = RecurringTaskService.parse_recurrence_pattern(recurrence_info)
    assert cron_expr == "0 0 15 */1 *", "Monthly pattern should return correct cron expression"


def test_parse_recurrence_pattern_yearly():
    """Test parsing yearly recurrence pattern"""
    recurrence_info = {
        'pattern': 'yearly',
        'month': 6,
        'day': 21  # June 21st
    }
    cron_expr = RecurringTaskService.parse_recurrence_pattern(recurrence_info)
    assert cron_expr == "0 0 21 6 *", "Yearly pattern should return correct cron expression"


def test_create_next_instance_basic():
    """Test creating next instance of a recurring task"""
    # Create a mock session
    session_mock = Mock(spec=Session)

    # Create a parent task
    parent_task = Task(
        id=1,
        title="Test Task",
        user_id="test-user",
        completed=False,
        priority="medium",
        due_date=datetime.now() + timedelta(days=1),
        recurrence_pattern='{"pattern": "daily", "frequency": 1}',
        recurrence_end_date=datetime.now() + timedelta(days=7),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Create a new recurring instance
    new_task = RecurringTaskService.create_next_instance(session_mock, parent_task, datetime.now() + timedelta(days=2))

    assert new_task is not None
    assert new_task.parent_task_id == parent_task.id
    assert new_task.title == "Test Task"
    assert new_task.completed is False


def test_get_next_occurrences():
    """Test calculating upcoming recurrence instances"""
    db_engine = create_engine("sqlite:///:memory:",
                              connect_args={"check_same_thread": False},
                              poolclass=StaticPool)

    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(db_engine)

    with Session(db_engine) as session:
        # Create test user
        user = create_test_user()
        session.add(user)
        session.commit()
        session.refresh(user)

        # Create parent recurring task
        parent_task = create_test_task(user_id=user.id)
        session.add(parent_task)
        session.commit()
        session.refresh(parent_task)

        # Test calculating next occurrences
        occurrences = RecurringTaskService.get_next_occurrences(
            session,
            parent_task.id,
            count=3
        )

        assert len(occurrences) == 3, f"Expected 3 occurrences, got {len(occurrences)}"

        # Check that occurrences are in chronological order
        for i in range(len(occurrences) - 1):
            assert occurrences[i] < occurrences[i + 1]


@patch('agents.event_publisher')
def test_creating_instance_publishes_event(event_publisher_mock):
    """Test that creating a recurring instance publishes a Kafka event"""
    session_mock = Mock(spec=Session)

    # Create parent task with recurrence
    parent_task = Task(
        id=1,
        title="Test Task",
        user_id="test-user",
        priority="medium",
        due_date=datetime.now() + timedelta(days=1),
        recurrence_pattern='{"pattern": "daily", "frequency": 1}',
        recurrence_end_date=datetime.now() + timedelta(days=7),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Mock the session.add and commit methods
    session_mock.commit = Mock()
    session_mock.refresh = Mock()

    # Ensure new task has the necessary attributes
    from datetime import timezone
    import json

    recurrence_data = json.loads(parent_task.recurrence_pattern)
    next_due = parent_task.due_date.replace(tzinfo=timezone.utc).astimezone(tz=None) if parent_task.due_date else None

    new_task = Task(
        id=2,
        title=parent_task.title,
        description=parent_task.description,
        user_id=parent_task.user_id,
        completed=False,
        priority=parent_task.priority,
        due_date=next_due,
        reminder_time=(next_due - timedelta(hours=1)) if next_due else None,
        recurrence_pattern=parent_task.recurrence_pattern,
        recurrence_end_date=parent_task.recurrence_end_date,
        parent_task_id=parent_task.id
    )

    # Mock session operations
    session_mock.add(new_task)

    # Call create method
    created_task = RecurringTaskService.create_next_instance(session_mock, parent_task, next_due)

    # Verify that event publisher method was called
    event_publisher_mock.publish_recurring_instance_created.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
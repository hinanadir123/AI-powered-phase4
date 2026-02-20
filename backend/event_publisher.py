"""
Main Event Publisher Integration Layer
Task: T5.3.2 - Implements phase5-spec.md Section 3.2.2 (Event Publishers)
Integrates with existing backend structure
"""

from typing import Dict, Any, Optional
from datetime import datetime

# Import from the events package
from .events.task_publisher import TaskEventPublisher
from .events.reminder_publisher import ReminderEventPublisher
from .events.state_management import DaprStateManager


class TaskEventIntegration:
    """
    Integrates event publishing with state management for the Todo API
    Manages the flow between state changes, event publishing, and Dapr components
    """

    def __init__(self, dapr_endpoint: str = "http://localhost:3500"):
        self.task_publisher = TaskEventPublisher(dapr_endpoint)
        self.reminder_publisher = ReminderEventPublisher(dapr_endpoint)
        self.state_manager = DaprStateManager(dapr_endpoint)

    def create_task_with_events(self, task_data: Dict[str, Any], user_id: str = None) -> bool:
        """Create a task and publish the appropriate events"""
        task_id = task_data.get('id')
        if not task_id:
            print("Task ID is required")
            return False

        # Save to state store first
        save_success = self.state_manager.save_task(task_id, task_data)
        if not save_success:
            print(f"Failed to save task {task_id} to state store")
            return False

        # Publish task created event
        correlation_id = f"create-task-{task_id}-{datetime.utcnow().timestamp()}"
        publish_success = self.task_publisher.publish_task_created(
            task_data, correlation_id=correlation_id, user_id=user_id
        )

        if publish_success:
            # Check for reminders and schedule if needed
            self._handle_reminder_scheduling(task_data, correlation_id, user_id)

        return publish_success

    def update_task_with_events(self, task_id: str, updates: Dict[str, Any], user_id: str = None) -> bool:
        """Update a task and publish change events"""
        # Get current task
        current_task = self.state_manager.get_task(task_id)
        if not current_task:
            print(f"Task {task_id} not found")
            return False

        # Merge updates
        updated_task = {**current_task, **updates}

        # Save updated task
        save_success = self.state_manager.update_task(task_id, updates)
        if not save_success:
            print(f"Failed to update task {task_id}")
            return False

        # Determine the type of update and publish appropriate event
        correlation_id = f"update-task-{task_id}-{datetime.utcnow().timestamp()}"

        # If status changed, publish status changed event
        if 'status' in updates and current_task.get('status') != updates['status']:
            event_success = self.task_publisher.publish_task_status_changed(
                updated_task, correlation_id=correlation_id, user_id=user_id
            )
        else:
            event_success = self.task_publisher.publish_task_updated(
                updated_task, correlation_id=correlation_id, user_id=user_id
            )

        if event_success:
            # Handle reminder scheduling if relevant fields changed
            if 'due_date' in updates or 'reminder' in updates:
                self._handle_reminder_scheduling(updated_task, correlation_id, user_id)

        return event_success

    def delete_task_with_events(self, task_id: str, user_id: str = None) -> bool:
        """Delete a task and publish deletion event"""
        # Publish deletion event first
        correlation_id = f"delete-task-{task_id}-{datetime.utcnow().timestamp()}"
        event_success = self.task_publisher.publish_task_deleted(
            task_id, correlation_id=correlation_id, user_id=user_id
        )

        if not event_success:
            print(f"Failed to publish deletion event for task {task_id}")
            # We still try to delete the task from state even if event publish fails
            # but we log the issue

        # Then delete from state store
        state_delete_success = self.state_manager.delete_task(task_id)

        return state_delete_success

    def _handle_reminder_scheduling(self, task_data: Dict[str, Any], correlation_id: str, user_id: str) -> None:
        """Handle reminder scheduling for tasks with due dates"""
        due_date = task_data.get('due_date')
        reminder_config = task_data.get('reminder', {})

        if due_date and reminder_config.get('enabled', False):
            # Calculate reminder time
            time_before = reminder_config.get('time_before', '1h')
            reminder_time = self._calculate_reminder_time(due_date, time_before)

            # Default channels if not specified
            channels = reminder_config.get('channels', ['push'])

            # Schedule reminder
            msg = f"Reminder: Task '{task_data.get('title', 'Untitled')}' is due soon!"
            self.reminder_publisher.publish_reminder_scheduled(
                task_data['id'],
                reminder_time,
                msg,
                channels,
                correlation_id=correlation_id,
                user_id=user_id
            )

    def _calculate_reminder_time(self, due_date: str, time_before: str) -> str:
        """Calculate the reminder time based on due date and time before reminder"""
        from datetime import datetime, timedelta

        due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00')).replace(tzinfo=None)

        # Parse time_before (like '1h', '2d', '30m')
        if time_before.endswith('h'):
            delta = timedelta(hours=int(time_before[:-1]))
        elif time_before.endswith('d'):
            delta = timedelta(days=int(time_before[:-1]))
        elif time_before.endswith('m'):
            delta = timedelta(minutes=int(time_before[:-1]))
        elif time_before.endswith('s'):
            delta = timedelta(seconds=int(time_before[:-1]))
        else:
            # Default to 1 hour before
            delta = timedelta(hours=1)

        reminder_time = due_datetime - delta

        # Don't schedule in the past
        from datetime import datetime as dt
        if reminder_time <= dt.utcnow():
            reminder_time = dt.utcnow() + timedelta(minutes=1)  # Schedule in 1 minute if already passed

        return reminder_time.isoformat() + 'Z'


# Global instance for use in API routes
task_event_integration = TaskEventIntegration()


# Integration test
if __name__ == "__main__":
    # Example usage
    integration = TaskEventIntegration()

    # Test task creation with events
    sample_task = {
        "id": "sample-task-123",
        "title": "Sample Task",
        "description": "This is a sample task for testing event integration",
        "status": "pending",
        "priority": "medium",
        "due_date": "2026-02-22T12:00:00Z",
        "reminder": {
            "enabled": True,
            "time_before": "2h",  # 2 hours before due time
            "channels": ["push", "email"]
        },
        "tags": ["test", "sample"],
        "created_by": "test-user"
    }

    print("Creating sample task with events...")
    success = integration.create_task_with_events(sample_task, user_id="test-user")
    print(f"Task creation with events: {success}")
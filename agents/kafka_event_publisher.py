"""
Advanced Event Publisher - Kafka Events
Task: T5.3.2 - Implements event publishing for advanced features
Spec Reference: phase5-spec.md Section 4.2 (Event Publishing)
Constitution: constitution.md v5.0

This file implements the Kafka publisher for advanced features:
- Recurring tasks events
- Reminder events
- Due date events
"""
import os
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class EventType(str, Enum):
    """Advanced task event types"""
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    # Advanced features events
    DUE_DATE_SET = "due_date.set"
    REMINDER_SCHEDULED = "reminder.scheduled"
    REMINDER_TRIGGERED = "reminder.triggered"
    RECURRING_TASK_CREATED = "recurring_task.created"
    RECURRING_TASK_UPDATED = "recurring_task.updated"
    RECURRING_TASK_COMPLETED = "recurring_task.completed"
    OVERDUE_TASK_DETECTED = "overdue_task.detected"
    PRIORITY_UPDATED = "priority.updated"
    TAGS_UPDATED = "tags.updated"
    TASK_RECALLED = "task.recalled"


class KafkaEventPublisher:
    """
    Advanced Event Publishing Service using Dapr HTTP API
    Implements Kafka event publishing for task-based microservices architecture
    All events follow Dapr Pub/Sub pattern via HTTP calls only (no direct Kafka SDK)
    """

    def __init__(self):
        self.dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
        self.dapr_url = f"http://localhost:{self.dapr_port}"
        self.pubsub_name = os.getenv("DAPR_PUBSUB_NAME", "pubsub-kafka")
        self.enabled = os.getenv("DAPR_ENABLED", "false").lower() == "true"

    def publish_event(self, topic: str, event_type: EventType, data: Dict[str, Any]) -> bool:
        """
        Publish event to Kafka via Dapr HTTP API

        Args:
            topic: Kafka topic name
            event_type: Type of event to publish
            data: Event data payload

        Returns:
            bool: True if published successfully
        """
        if not self.enabled:
            print(f"[DAPR DISABLED] Would publish {event_type.value} to {topic}: {data}")
            return True

        try:
            payload = {
                "event_type": event_type.value,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }

            url = f"{self.dapr_url}/v1.0/publish/{self.pubsub_name}/{topic}"

            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 204:
                print(f"[EVENT PUBLISHED] {event_type.value} to {topic}")
                return True
            else:
                print(f"[EVENT FAILED] {event_type.value} to {topic}: {response.status_code} {response.text}")
                return False

        except Exception as e:
            print(f"[EVENT ERROR] Publishing {event_type.value} to {topic}: {e}")
            return False

    # Advanced Features Event Publishers

    def publish_due_date_set(self, task_id: int, due_date: str, user_id: str, metadata: Optional[Dict] = None):
        """Publish due date set event"""
        return self.publish_event(
            "task-events",
            EventType.DUE_DATE_SET,
            {
                "task_id": task_id,
                "due_date": due_date,
                "user_id": user_id,
                "metadata": metadata or {}
            }
        )

    def publish_reminder_scheduled(self, task_id: int, reminder_time: str, user_id: str, metadata: Optional[Dict] = None):
        """Publish reminder scheduled event"""
        return self.publish_event(
            "reminders",
            EventType.REMINDER_SCHEDULED,
            {
                "task_id": task_id,
                "reminder_time": reminder_time,
                "user_id": user_id,
                "metadata": metadata or {}
            }
        )

    def publish_reminder_triggered(self, task_id: int, due_date: str, reminder_time: str, user_id: str, metadata: Optional[Dict] = None):
        """Publish reminder triggered event"""
        return self.publish_event(
            "reminders",
            EventType.REMINDER_TRIGGERED,
            {
                "task_id": task_id,
                "due_date": due_date,
                "reminder_time": reminder_time,
                "user_id": user_id,
                "metadata": metadata or {}
            }
        )

    def publish_recurring_task_created(self, task_id: int, parent_task_id: int, recurrence_pattern: str, user_id: str, metadata: Optional[Dict] = None):
        """Publish recurring task created event"""
        return self.publish_event(
            "task-events",
            EventType.RECURRING_TASK_CREATED,
            {
                "task_id": task_id,
                "parent_task_id": parent_task_id,
                "recurrence_pattern": recurrence_pattern,
                "user_id": user_id,
                "metadata": metadata or {}
            }
        )

    def publish_recurring_task_updated(self, task_id: int, recurrence_pattern: str, user_id: str, metadata: Optional[Dict] = None):
        """Publish recurring task updated event"""
        return self.publish_event(
            "task-events",
            EventType.RECURRING_TASK_UPDATED,
            {
                "task_id": task_id,
                "recurrence_pattern": recurrence_pattern,
                "user_id": user_id,
                "metadata": metadata or {}
            }
        )

    def publish_recurring_task_completed(self, task_id: int, parent_task_id: int, user_id: str, metadata: Optional[Dict] = None):
        """Publish recurring task completed event"""
        return self.publish_event(
            "task-events",
            EventType.RECURRING_TASK_COMPLETED,
            {
                "task_id": task_id,
                "parent_task_id": parent_task_id,
                "user_id": user_id,
                "metadata": metadata or {}
            }
        )

    def publish_overdue_task_detected(self, task_id: int, due_date: str, user_id: str, metadata: Optional[Dict] = None):
        """Publish overdue task detected event"""
        return self.publish_event(
            "task-events",
            EventType.OVERDUE_TASK_DETECTED,
            {
                "task_id": task_id,
                "due_date": due_date,
                "user_id": user_id,
                "metadata": metadata or {}
            }
        )

    def publish_priority_updated(self, task_id: int, old_priority: str, new_priority: str, user_id: str, metadata: Optional[Dict] = None):
        """Publish priority updated event"""
        return self.publish_event(
            "task-events",
            EventType.PRIORITY_UPDATED,
            {
                "task_id": task_id,
                "old_priority": old_priority,
                "new_priority": new_priority,
                "user_id": user_id,
                "metadata": metadata or {}
            }
        )

    def publish_tags_updated(self, task_id: int, added_tags: list, removed_tags: list, user_id: str, metadata: Optional[Dict] = None):
        """Publish tags updated event"""
        return self.publish_event(
            "task-events",
            EventType.TAGS_UPDATED,
            {
                "task_id": task_id,
                "added_tags": added_tags,
                "removed_tags": removed_tags,
                "user_id": user_id,
                "metadata": metadata or {}
            }
        )

    def publish_task_recalled(self, task_id: int, recall_reason: str, user_id: str, metadata: Optional[Dict] = None):
        """Publish task recalled event"""
        return self.publish_event(
            "task-events",
            EventType.TASK_RECALLED,
            {
                "task_id": task_id,
                "recall_reason": recall_reason,
                "user_id": user_id,
                "metadata": metadata or {}
            }
        )


# Create global event publisher instance
event_publisher = KafkaEventPublisher()

# Initialize as the main event publisher for the backend
def get_event_publisher():
    return event_publisher
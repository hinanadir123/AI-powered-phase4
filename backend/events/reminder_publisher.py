"""
Reminder Event Publisher - Publishes reminder-related events to Kafka via Dapr Pub/Sub
Task: T5.3.2 - Implements phase5-spec.md Section 3.2.2 (Event Publishers)
Constitution: constitution.md v5.0 Section 2.3 (No Direct Kafka/PostgreSQL SDK imports)
"""

import json
import uuid
import requests
from datetime import datetime
from typing import Dict, Any


class ReminderEventPublisher:
    """Publishes reminder-related events to Kafka via Dapr Pub/Sub"""

    def __init__(self, dapr_endpoint: str = "http://localhost:3500"):
        self.dapr_endpoint = dapr_endpoint
        self.pubsub_name = "kafka-pubsub"
        self.reminders_topic = "reminders"

    def _create_cloudevent(self, event_type: str, reminder_data: Dict[Any, Any], correlation_id: str = None, user_id: str = None):
        """Create a CloudEvents v1.0 compliant event"""
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        event_id = f"reminder-{event_type}-{reminder_data.get('task_id', uuid.uuid4())}-{datetime.utcnow().timestamp()}"

        return {
            "specversion": "1.0",
            "id": event_id,
            "source": "/todo-backend/reminders",
            "type": f"reminder.{event_type}",
            "datacontenttype": "application/json",
            "time": datetime.utcnow().isoformat() + "Z",
            "subject": f"reminder:{reminder_data.get('task_id', 'unknown')}",
            "data": reminder_data,
            "correlationId": correlation_id,
            "userId": user_id
        }

    def publish_reminder_scheduled(self, task_id: str, reminder_time: str, message: str,
                                 channels: list, correlation_id: str = None, user_id: str = None) -> bool:
        """Publish reminder scheduled event to Kafka"""
        try:
            reminder_data = {
                "task_id": task_id,
                "reminder_time": reminder_time,
                "message": message,
                "channels": channels,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            event = self._create_cloudevent("scheduled", reminder_data, correlation_id, user_id)
            return self._publish_event(event)
        except Exception as e:
            print(f"Error publishing reminder scheduled event: {e}")
            return False

    def publish_reminder_triggered(self, task_id: str, message: str, channels: list,
                                 correlation_id: str = None, user_id: str = None) -> bool:
        """Publish reminder triggered event to Kafka"""
        try:
            reminder_data = {
                "task_id": task_id,
                "message": message,
                "channels": channels,
                "triggered_at": datetime.utcnow().isoformat() + "Z"
            }
            event = self._create_cloudevent("triggered", reminder_data, correlation_id, user_id)
            return self._publish_event(event)
        except Exception as e:
            print(f"Error publishing reminder triggered event: {e}")
            return False

    def publish_reminder_cancelled(self, task_id: str, reason: str,
                                 correlation_id: str = None, user_id: str = None) -> bool:
        """Publish reminder cancelled event to Kafka"""
        try:
            reminder_data = {
                "task_id": task_id,
                "reason": reason,
                "cancelled_at": datetime.utcnow().isoformat() + "Z"
            }
            event = self._create_cloudevent("cancelled", reminder_data, correlation_id, user_id)
            return self._publish_event(event)
        except Exception as e:
            print(f"Error publishing reminder cancelled event: {e}")
            return False

    def publish_reminder_failed(self, task_id: str, error_message: str, error_type: str,
                              correlation_id: str = None, user_id: str = None) -> bool:
        """Publish reminder failed processing event to Kafka"""
        try:
            reminder_data = {
                "task_id": task_id,
                "error_message": error_message,
                "error_type": error_type,
                "failed_at": datetime.utcnow().isoformat() + "Z"
            }
            event = self._create_cloudevent("failed", reminder_data, correlation_id, user_id)
            return self._publish_event(event)
        except Exception as e:
            print(f"Error publishing reminder failed event: {e}")
            return False

    def _publish_event(self, event: Dict) -> bool:
        """Publish event to Dapr Pub/Sub"""
        url = f"{self.dapr_endpoint}/v1.0/publish/{self.pubsub_name}/{self.reminders_topic}"

        try:
            response = requests.post(
                url,
                json=event,
                headers={"Content-Type": "application/json", "traceparent": f"00-{uuid.uuid4()}-{uuid.uuid4()}-01"},
                timeout=30
            )

            if response.status_code == 200:
                print(f"Reminder event published successfully: {event['type']} - {event['id']}")
                return True
            else:
                print(f"Failed to publish reminder event: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Network error publishing reminder event: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error publishing reminder event: {e}")
            return False


# Test the publisher
if __name__ == "__main__":
    publisher = ReminderEventPublisher()

    # Test reminder schedule
    success = publisher.publish_reminder_scheduled(
        task_id="task-12345",
        reminder_time="2026-02-20T09:00:00Z",
        message="Task is due soon: Complete Dapr Integration",
        channels=["push", "email"],
        user_id="user-001"
    )
    print(f"Reminder scheduled event published: {success}")
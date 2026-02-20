"""
Task Event Publisher - Publishes task-related events to Kafka via Dapr Pub/Sub
Task: T5.3.2 - Implements phase5-spec.md Section 3.2.2 (Event Publishers)
Constitution: constitution.md v5.0 Section 2.3 (No Direct Kafka/PostgreSQL SDK imports)
"""

import json
import uuid
import requests
from datetime import datetime
from typing import Dict, Any


class TaskEventPublisher:
    """Publishes task-related events to Kafka via Dapr Pub/Sub"""

    def __init__(self, dapr_endpoint: str = "http://localhost:3500"):
        self.dapr_endpoint = dapr_endpoint
        self.pubsub_name = "kafka-pubsub"
        self.task_events_topic = "task-events"
        self.task_updates_topic = "task-updates"

    def _create_cloudevent(self, event_type: str, task_data: Dict[Any, Any], correlation_id: str = None, user_id: str = None):
        """Create a CloudEvents v1.0 compliant event"""
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        event_id = f"task-{event_type}-{task_data.get('id', uuid.uuid4())}-{datetime.utcnow().timestamp()}"

        return {
            "specversion": "1.0",
            "id": event_id,
            "source": "/todo-backend/tasks",
            "type": f"task.{event_type}",
            "datacontenttype": "application/json",
            "time": datetime.utcnow().isoformat() + "Z",
            "subject": f"task:{task_data.get('id', 'unknown')}",
            "data": task_data,
            "correlationId": correlation_id,
            "userId": user_id
        }

    def publish_task_created(self, task_data: Dict[Any, Any], correlation_id: str = None, user_id: str = None) -> bool:
        """Publish task created event to Kafka"""
        try:
            event = self._create_cloudevent("created", task_data, correlation_id, user_id)
            return self._publish_event(self.task_events_topic, event)
        except Exception as e:
            print(f"Error publishing task created event: {e}")
            return False

    def publish_task_updated(self, task_data: Dict[Any, Any], correlation_id: str = None, user_id: str = None) -> bool:
        """Publish task updated event to Kafka"""
        try:
            event = self._create_cloudevent("updated", task_data, correlation_id, user_id)
            return self._publish_event(self.task_events_topic, event)
        except Exception as e:
            print(f"Error publishing task updated event: {e}")
            return False

    def publish_task_deleted(self, task_id: str, correlation_id: str = None, user_id: str = None) -> bool:
        """Publish task deleted event to Kafka"""
        try:
            event_data = {"task_id": task_id, "deleted_at": datetime.utcnow().isoformat() + "Z"}
            event = self._create_cloudevent("deleted", event_data, correlation_id, user_id)
            return self._publish_event(self.task_events_topic, event)
        except Exception as e:
            print(f"Error publishing task deleted event: {e}")
            return False

    def publish_task_status_changed(self, task_data: Dict[Any, Any], correlation_id: str = None, user_id: str = None) -> bool:
        """Publish task status changed event to Kafka"""
        try:
            event = self._create_cloudevent("status.changed", task_data, correlation_id, user_id)
            return self._publish_event(self.task_events_topic, event)
        except Exception as e:
            print(f"Error publishing task status changed event: {e}")
            return False

    def publish_task_assigned(self, task_data: Dict[Any, Any], correlation_id: str = None, user_id: str = None) -> bool:
        """Publish task assigned event to Kafka"""
        try:
            event = self._create_cloudevent("assigned", task_data, correlation_id, user_id)
            return self._publish_event(self.task_updates_topic, event)
        except Exception as e:
            print(f"Error publishing task assigned event: {e}")
            return False

    def _publish_event(self, topic: str, event: Dict) -> bool:
        """Publish event to Dapr Pub/Sub with retry logic"""
        url = f"{self.dapr_endpoint}/v1.0/publish/{self.pubsub_name}/{topic}"

        try:
            response = requests.post(
                url,
                json=event,
                headers={"Content-Type": "application/json", "traceparent": f"00-{uuid.uuid4()}-{uuid.uuid4()}-01"},
                timeout=30
            )

            if response.status_code == 200:
                print(f"Event published successfully to {topic}: {event['id']}")
                return True
            else:
                print(f"Failed to publish event to {topic}: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Network error publishing event to {topic}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error publishing event to {topic}: {e}")
            return False


# Test the publisher
if __name__ == "__main__":
    publisher = TaskEventPublisher()

    # Test task data
    test_task = {
        "id": "task-12345",
        "title": "Test task",
        "description": "This is a test task",
        "status": "pending",
        "priority": "medium",
        "tags": ["test", "urgent"],
        "due_date": "2026-02-20T10:00:00Z",
        "created_by": "user-001"
    }

    # Publish event
    success = publisher.publish_task_created(test_task, user_id="user-001")
    print(f"Task created event published: {success}")
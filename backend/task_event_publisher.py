# Task: T5.3.2 - Implement Kafka Publisher for Task Events
# Spec Reference: phase5-spec.md Section 3.2.1, Section 4.2 (Event Flow)
# Constitution: constitution.md v5.0 Section 2.3 (Event-Driven Architecture Requirements)
#
# This module implements Kafka event publishing using Dapr Pub/Sub HTTP API.
# NO direct Kafka SDK imports - all communication via Dapr sidecar.
#
# Event Types:
# - task.created: New task created
# - task.updated: Task modified
# - task.deleted: Task removed
# - task.completed: Task marked as complete
#
# CloudEvents v1.0 format is used for all events.
#
# Version: 1.0
# Date: 2026-02-15

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class TaskEventPublisher:
    """
    Publishes task events to Kafka via Dapr Pub/Sub HTTP API.

    Uses Dapr sidecar at localhost:3500 to publish events to Kafka topics.
    All events follow CloudEvents v1.0 specification.
    """

    def __init__(self, dapr_http_port: int = 3500, pubsub_name: str = "pubsub-kafka"):
        """
        Initialize the Task Event Publisher.

        Args:
            dapr_http_port: Dapr sidecar HTTP port (default: 3500)
            pubsub_name: Name of Dapr Pub/Sub component (default: pubsub-kafka)
        """
        self.dapr_url = f"http://localhost:{dapr_http_port}"
        self.pubsub_name = pubsub_name
        self.topic_name = "task-events"

    def _create_cloud_event(
        self,
        event_type: str,
        task_id: str,
        data: Dict[str, Any],
        source: str = "todo-backend"
    ) -> Dict[str, Any]:
        """
        Create a CloudEvents v1.0 formatted event.

        Args:
            event_type: Type of event (task.created, task.updated, etc.)
            task_id: ID of the task
            data: Event payload data
            source: Source of the event

        Returns:
            CloudEvents formatted dictionary
        """
        return {
            "specversion": "1.0",
            "type": event_type,
            "source": source,
            "id": str(uuid4()),
            "time": datetime.utcnow().isoformat() + "Z",
            "datacontenttype": "application/json",
            "subject": f"tasks/{task_id}",
            "data": data
        }

    def _publish_event(self, event: Dict[str, Any]) -> bool:
        """
        Publish event to Kafka via Dapr Pub/Sub HTTP API.

        Args:
            event: CloudEvents formatted event

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.dapr_url}/v1.0/publish/{self.pubsub_name}/{self.topic_name}"

        try:
            response = requests.post(
                url,
                json=event,
                headers={"Content-Type": "application/json"},
                timeout=5
            )

            if response.status_code == 200:
                logger.info(f"✅ Published event: {event['type']} for task {event['subject']}")
                return True
            else:
                logger.error(f"❌ Failed to publish event: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error publishing event: {str(e)}")
            return False

    def publish_task_created(self, task: Dict[str, Any]) -> bool:
        """
        Publish task.created event.

        Args:
            task: Task data dictionary

        Returns:
            True if successful, False otherwise
        """
        event = self._create_cloud_event(
            event_type="task.created",
            task_id=task["id"],
            data={
                "task_id": task["id"],
                "title": task["title"],
                "description": task.get("description"),
                "priority": task.get("priority", "medium"),
                "tags": task.get("tags", []),
                "due_date": task.get("due_date"),
                "recurrence": task.get("recurrence"),
                "reminder": task.get("reminder"),
                "user_id": task["user_id"],
                "created_at": task["created_at"]
            }
        )
        return self._publish_event(event)

    def publish_task_updated(self, task: Dict[str, Any], changes: Dict[str, Any]) -> bool:
        """
        Publish task.updated event.

        Args:
            task: Updated task data dictionary
            changes: Dictionary of changed fields

        Returns:
            True if successful, False otherwise
        """
        event = self._create_cloud_event(
            event_type="task.updated",
            task_id=task["id"],
            data={
                "task_id": task["id"],
                "changes": changes,
                "current_state": {
                    "title": task["title"],
                    "description": task.get("description"),
                    "status": task["status"],
                    "priority": task.get("priority", "medium"),
                    "tags": task.get("tags", []),
                    "due_date": task.get("due_date"),
                    "recurrence": task.get("recurrence"),
                    "reminder": task.get("reminder")
                },
                "user_id": task["user_id"],
                "updated_at": task.get("updated_at", datetime.utcnow().isoformat())
            }
        )
        return self._publish_event(event)

    def publish_task_completed(self, task: Dict[str, Any]) -> bool:
        """
        Publish task.completed event.

        Args:
            task: Completed task data dictionary

        Returns:
            True if successful, False otherwise
        """
        event = self._create_cloud_event(
            event_type="task.completed",
            task_id=task["id"],
            data={
                "task_id": task["id"],
                "title": task["title"],
                "priority": task.get("priority", "medium"),
                "tags": task.get("tags", []),
                "recurrence": task.get("recurrence"),
                "parent_task_id": task.get("parent_task_id"),
                "user_id": task["user_id"],
                "completed_at": task.get("completed_at", datetime.utcnow().isoformat())
            }
        )
        return self._publish_event(event)

    def publish_task_deleted(self, task_id: str, user_id: str) -> bool:
        """
        Publish task.deleted event.

        Args:
            task_id: ID of deleted task
            user_id: ID of user who owns the task

        Returns:
            True if successful, False otherwise
        """
        event = self._create_cloud_event(
            event_type="task.deleted",
            task_id=task_id,
            data={
                "task_id": task_id,
                "user_id": user_id,
                "deleted_at": datetime.utcnow().isoformat()
            }
        )
        return self._publish_event(event)


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Initialize publisher
    publisher = TaskEventPublisher()

    # Example: Publish task created event
    task_data = {
        "id": "task-123",
        "title": "Complete Phase 5 implementation",
        "description": "Implement all advanced features",
        "priority": "high",
        "tags": ["development", "phase5"],
        "due_date": "2026-02-20T10:00:00Z",
        "recurrence": {
            "enabled": True,
            "interval": "weekly",
            "frequency": 1,
            "days": ["monday"]
        },
        "reminder": {
            "enabled": True,
            "time_before": "1h",
            "channels": ["email"]
        },
        "user_id": "user-456",
        "created_at": datetime.utcnow().isoformat()
    }

    publisher.publish_task_created(task_data)

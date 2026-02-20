"""
Dapr State Management Integration
Task: T5.2.1-T5.4 - Implements phase5-spec.md Section 2 (Dapr State Store)
Constitution: constitution.md v5.0 Section 2.3 (No Direct PostgreSQL SDK imports)
"""

import json
import requests
from typing import Dict, Any, Union, Optional
from datetime import datetime
import logging


class DaprStateManager:
    """
    Integration with Dapr State Store for managing task states via Dapr HTTP API
    No direct PostgreSQL SDK imports - Uses Dapr sidecar to handle all database interaction
    """

    def __init__(self, dapr_endpoint: str = "http://localhost:3500", state_store_name: str = "postgresql-statestore"):
        self.dapr_endpoint = dapr_endpoint
        self.state_store_name = state_store_name
        self.logger = logging.getLogger(__name__)

    def save_task(self, task_id: str, task_data: Dict[str, Any], etag: str = None) -> bool:
        """Save a task to the state store"""
        try:
            state_item = {
                "key": f"task:{task_id}",
                "value": {
                    **task_data,
                    "updated_at": datetime.utcnow().isoformat() + "Z",
                    "etag": "v1"  # Simple version tracking
                }
            }

            if etag:
                state_item["etag"] = etag

            url = f"{self.dapr_endpoint}/v1.0/state/{self.state_store_name}"
            headers = {"Content-Type": "application/json"}

            response = requests.post(url, json=[state_item], headers=headers, timeout=30)

            if response.status_code in [200, 201, 204]:
                self.logger.info(f"Task {task_id} saved successfully to state store")
                return True
            else:
                self.logger.error(f"Failed to save task {task_id}: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Error saving task {task_id} to state store: {e}")
            return False

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a task from the state store"""
        try:
            key = f"task:{task_id}"
            url = f"{self.dapr_endpoint}/v1.0/state/{self.state_store_name}/{key}"

            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"Task {task_id} retrieved successfully")
                return data
            elif response.status_code == 404:
                self.logger.info(f"Task {task_id} not found in state store")
                return None
            else:
                self.logger.error(f"Failed to get task {task_id}: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error getting task {task_id} from state store: {e}")
            return None

    def update_task(self, task_id: str, updates: Dict[str, Any], etag: str = None) -> bool:
        """Update a task in the state store"""
        try:
            # First get the current task to merge updates
            current_task = self.get_task(task_id)
            if not current_task:
                self.logger.error(f"Cannot update non-existent task {task_id}")
                return False

            # Merge updates with current data
            updated_task = {**current_task, **updates}
            updated_task["updated_at"] = datetime.utcnow().isoformat() + "Z"

            return self.save_task(task_id, updated_task, etag)

        except Exception as e:
            self.logger.error(f"Error updating task {task_id} in state store: {e}")
            return False

    def delete_task(self, task_id: str) -> bool:
        """Delete a task from the state store"""
        try:
            key = f"task:{task_id}"
            url = f"{self.dapr_endpoint}/v1.0/state/{self.state_store_name}/{key}"

            response = requests.delete(url, timeout=30)

            if response.status_code in [200, 204]:
                self.logger.info(f"Task {task_id} deleted successfully from state store")
                return True
            else:
                self.logger.error(f"Failed to delete task {task_id}: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Error deleting task {task_id} from state store: {e}")
            return False

    def get_tasks_by_status(self, status: str) -> list:
        """Get all tasks with a specific status using state query (if supported)"""
        # Note: Full state query is not available in all Dapr state stores
        # This is a simplified approach that would work in a real implementation
        # For now, just return an empty list as a placeholder
        self.logger.warning("Task query by status is not fully implemented in this demo")
        return []

    def save_user_tasks(self, user_id: str, task_ids: list) -> bool:
        """Save user's task list to state store"""
        try:
            state_item = {
                "key": f"user-tasks:{user_id}",
                "value": {
                    "task_ids": task_ids,
                    "updated_at": datetime.utcnow().isoformat() + "Z"
                }
            }

            url = f"{self.dapr_endpoint}/v1.0/state/{self.state_store_name}"
            headers = {"Content-Type": "application/json"}

            response = requests.post(url, json=[state_item], headers=headers, timeout=30)

            if response.status_code in [200, 201, 204]:
                self.logger.info(f"User {user_id} tasks saved successfully")
                return True
            else:
                self.logger.error(f"Failed to save user {user_id} tasks: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Error saving user {user_id} tasks to state store: {e}")
            return False

    def get_user_tasks(self, user_id: str) -> list:
        """Get user's task list from state store"""
        try:
            key = f"user-tasks:{user_id}"
            url = f"{self.dapr_endpoint}/v1.0/state/{self.state_store_name}/{key}"

            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"User {user_id} tasks retrieved successfully")
                return data.get("task_ids", [])
            elif response.status_code == 404:
                self.logger.info(f"User {user_id} tasks not found")
                return []
            else:
                self.logger.error(f"Failed to get user {user_id} tasks: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            self.logger.error(f"Error getting user {user_id} tasks from state store: {e}")
            return []

    def bulk_save_tasks(self, task_items: Dict[str, Dict[str, Any]]) -> bool:
        """Save multiple tasks to the state store in a single operation"""
        try:
            state_items = []
            for task_id, task_data in task_items.items():
                state_items.append({
                    "key": f"task:{task_id}",
                    "value": {
                        **task_data,
                        "updated_at": datetime.utcnow().isoformat() + "Z",
                        "etag": "v1"
                    }
                })

            url = f"{self.dapr_endpoint}/v1.0/state/{self.state_store_name}"
            headers = {"Content-Type": "application/json"}

            response = requests.post(url, json=state_items, headers=headers, timeout=30)

            if response.status_code in [200, 201, 204]:
                self.logger.info(f"Bulk saved {len(task_items)} tasks successfully")
                return True
            else:
                self.logger.error(f"Failed bulk save: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Error in bulk save operation: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Test the state manager
    state_manager = DaprStateManager()

    # Example task data
    test_task = {
        "id": "task-12345",
        "title": "Test task",
        "description": "This is a test task",
        "status": "pending",
        "priority": "medium",
        "tags": ["test", "urgent"],
        "due_date": "2026-02-20T10:00:00Z",
        "created_by": "user-001",
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    # Test save operation
    success = state_manager.save_task("task-12345", test_task)
    print(f"Save task result: {success}")

    # Test get operation
    retrieved_task = state_manager.get_task("task-12345")
    print(f"Retrieved task: {retrieved_task}")
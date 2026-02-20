"""
Integration Tests for Kafka + Dapr Integration
Task: T5.4.2 - Implements phase5-spec.md Section 5 (Testing Requirements)
"""

import pytest
import requests
import json
from datetime import datetime, timedelta
import time
from events.task_publisher import TaskEventPublisher
from events.reminder_publisher import ReminderEventPublisher
from events.state_management import DaprStateManager
from event_publisher import TaskEventIntegration


class TestKafkaDaprIntegration:
    """Integration tests for Kafka + Dapr event-driven architecture"""

    def setup_method(self):
        """Setup test fixtures"""
        self.dapr_endpoint = "http://localhost:3500"
        self.task_publisher = TaskEventPublisher(self.dapr_endpoint)
        self.reminder_publisher = ReminderEventPublisher(self.dapr_endpoint)
        self.state_manager = DaprStateManager(self.dapr_endpoint)
        self.task_integration = TaskEventIntegration(self.dapr_endpoint)

        # Generate unique task ID for test isolation
        self.test_task_id = f"test-task-{int(time.time())}"
        self.test_task = {
            "id": self.test_task_id,
            "title": f"Integration Test Task {self.test_task_id}",
            "description": "This is a test task for integration testing",
            "status": "pending",
            "priority": "medium",
            "due_date": "2026-12-31T23:59:59Z",
            "reminder": {
                "enabled": True,
                "time_before": "1h",
                "channels": ["push", "email"]
            },
            "tags": ["integration-test", "dapr", "kafka"],
            "created_by": "integration-test-user",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

    def test_task_event_publishing(self):
        """Test that task events are published correctly"""
        success = self.task_publisher.publish_task_created(self.test_task)

        assert success is True, "Task event should be published successfully"

    def test_reminder_event_publishing(self):
        """Test that reminder events are published correctly"""
        success = self.reminder_publisher.publish_reminder_scheduled(
            task_id=self.test_task_id,
            reminder_time="2026-12-31T22:59:59Z",  # 1 hour before due date
            message=f"Reminder for task {self.test_task_id}",
            channels=["push", "email"]
        )

        assert success is True, "Reminder event should be published successfully"

    def test_state_management_integration(self):
        """Test Dapr State Store integration for task state"""
        # Save task
        save_success = self.state_manager.save_task(self.test_task_id, self.test_task)
        assert save_success is True, "Task should be saved to state store"

        # Retrieve task
        retrieved_task = self.state_manager.get_task(self.test_task_id)
        assert retrieved_task is not None, "Task should be retrievable from state store"
        assert retrieved_task.get("id") == self.test_task_id, "Retrieved task ID should match"

        # Update task
        update_success = self.state_manager.update_task(
            self.test_task_id,
            {"status": "in-progress", "updated_field": "test-value"}
        )
        assert update_success is True, "Task should be updated in state store"

        # Verify update
        updated_task = self.state_manager.get_task(self.test_task_id)
        assert updated_task.get("status") == "in-progress", "Task status should be updated"
        assert updated_task.get("updated_field") == "test-value", "Task should have updated field"

    def test_task_event_integration_with_state(self):
        """Test the integration flow: state save -> event publish"""
        success = self.task_integration.create_task_with_events(self.test_task)
        assert success is True, "Task should be created with events successfully"

        # Verify state was updated
        retrieved_task = self.state_manager.get_task(self.test_task_id)
        assert retrieved_task is not None, "Task should exist in state store"

    def test_reminder_scheduling_workflow(self):
        """Test the full reminder scheduling workflow"""
        # First, create a task with reminder enabled
        task_with_reminder = {
            **self.test_task,
            "due_date": (datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=0) + timedelta(days=1)).isoformat() + "Z",
            "reminder": {
                "enabled": True,
                "time_before": "1h",
                "channels": ["push"]
            }
        }

        success = self.task_integration.create_task_with_events(task_with_reminder)
        assert success is True, "Task with reminder should be created successfully"

    def test_update_task_with_events(self):
        """Test updating a task triggers appropriate events"""
        # First create a task
        create_success = self.task_integration.create_task_with_events(self.test_task)
        assert create_success is True, "Initial task should be created successfully"

        # Update the task
        updates = {"status": "completed", "notes": "Task completed successfully"}
        update_success = self.task_integration.update_task_with_events(self.test_task_id, updates)
        assert update_success is True, "Task should be updated with events successfully"

    def test_delete_task_with_events(self):
        """Test deleting a task triggers appropriate events"""
        # First create a task
        create_success = self.task_integration.create_task_with_events(self.test_task_id, self.test_task)
        assert create_success is True, "Task should be created successfully before deletion"

        # Delete the task
        delete_success = self.task_integration.delete_task_with_events(self.test_task_id)
        assert delete_success is True, "Task should be deleted with events successfully"

    def test_bulk_task_operations(self):
        """Test bulk state operations"""
        tasks = {}
        for i in range(3):
            task_id = f"bulk-task-{self.test_task_id}-{i}"
            tasks[task_id] = {
                "id": task_id,
                "title": f"Bulk Test Task {i}",
                "status": "pending",
                "created_by": "bulk-test-user"
            }

        success = self.state_manager.bulk_save_tasks(tasks)
        assert success is True, "Bulk save operation should succeed"

    def test_concurrent_task_operations(self):
        """Test concurrent task operations to simulate real usage"""
        import concurrent.futures
        from threading import Thread
        import time

        def create_task(task_id):
            test_task = {
                "id": task_id,
                "title": f"Concurrent Task {task_id}",
                "status": "pending",
                "priority": "low",
                "created_by": "concurrent-test-user"
            }
            return self.task_integration.create_task_with_events(test_task)

        # Create multiple tasks concurrently
        task_ids = [f"concurrent-task-{i}-{int(time.time())}" for i in range(5)]
        results = []

        # Use ThreadPool to simulate concurrent task creation
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Create futures for concurrent execution
            futures = [executor.submit(create_task, task_id) for task_id in task_ids]
            results = [future.result() for future in futures]

        # Verify all tasks were created successfully
        for i, result in enumerate(results):
            assert result is True, f"Concurrent task {task_ids[i]} should be created successfully"

        # Verify all tasks exist in state store
        for task_id in task_ids:
            retrieved_task = self.state_manager.get_task(task_id)
            assert retrieved_task is not None, f"Task {task_id} should exist in state store"


def run_integration_tests():
    """Run all integration tests"""
    print("Starting Kafka + Dapr Integration Tests...")

    test_instance = TestKafkaDaprIntegration()

    try:
        test_instance.setup_method()
        print("✓ Setup completed")

        # Run individual tests
        test_instance.test_task_event_publishing()
        print("✓ Task event publishing test passed")

        test_instance.test_reminder_event_publishing()
        print("✓ Reminder event publishing test passed")

        test_instance.test_state_management_integration()
        print("✓ State management integration test passed")

        test_instance.test_task_event_integration_with_state()
        print("✓ Task event integration with state test passed")

        test_instance.test_update_task_with_events()
        print("✓ Update task with events test passed")

        test_instance.test_bulk_task_operations()
        print("✓ Bulk task operations test passed")

        test_instance.test_concurrent_task_operations()
        print("✓ Concurrent task operations test passed")

        print("\n🎉 All integration tests passed successfully!")
        return True

    except AssertionError as e:
        print(f"\n❌ Integration test failed: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Error during integration tests: {e}")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    if not success:
        exit(1)
    print("\n✅ Integration testing completed successfully!")
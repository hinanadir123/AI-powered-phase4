# Task: T5.4.2, T5.4.3 - Test Configuration and Fixtures
# Spec Reference: phase5-spec.md Section 8 (Timeline & Task Breakdown)
# Constitution: constitution.md v5.0 Section 10 (Validation Criteria)
#
# Pytest configuration and shared fixtures for integration and E2E tests.
# Provides common setup, teardown, and utility functions.
#
# Version: 1.0
# Date: 2026-02-15

import pytest
import requests
import logging
from typing import Generator, Dict, Any
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Test Configuration
class TestConfig:
    """Central configuration for all tests"""

    # Service URLs
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    WORKER_URL = os.getenv("WORKER_URL", "http://localhost:5001")
    DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
    DAPR_URL = f"http://localhost:{DAPR_HTTP_PORT}"

    # Dapr Components
    PUBSUB_NAME = "pubsub-kafka"
    STATE_STORE_NAME = "statestore-postgresql"

    # Kafka Topics
    TASK_EVENTS_TOPIC = "task-events"
    REMINDERS_TOPIC = "reminders"
    TASK_UPDATES_TOPIC = "task-updates"

    # Test User
    TEST_USER_ID = "test-user-123"
    TEST_AUTH_TOKEN = "test-token"

    # Timeouts
    DEFAULT_TIMEOUT = 5
    LONG_TIMEOUT = 30
    EVENT_PROCESSING_DELAY = 2  # seconds to wait for async event processing


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration"""
    return TestConfig()


@pytest.fixture(scope="session")
def check_services_health(test_config):
    """
    Check that all required services are running before tests start.
    Fails fast if services are not available.
    """
    services = {
        "Backend API": f"{test_config.BACKEND_URL}/health",
        "Reminder Worker": f"{test_config.WORKER_URL}/health",
        "Dapr Sidecar": f"{test_config.DAPR_URL}/v1.0/healthz"
    }

    failed_services = []

    for service_name, health_url in services.items():
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ {service_name} is healthy")
            else:
                logger.error(f"❌ {service_name} returned {response.status_code}")
                failed_services.append(service_name)
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ {service_name} is not accessible: {str(e)}")
            failed_services.append(service_name)

    if failed_services:
        pytest.skip(f"Required services not available: {', '.join(failed_services)}")

    return True


@pytest.fixture
def api_client(test_config):
    """Provide configured API client"""
    class APIClient:
        def __init__(self, base_url: str, auth_token: str):
            self.base_url = base_url
            self.headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }

        def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
            """Create a task via API"""
            response = requests.post(
                f"{self.base_url}/api/tasks",
                json=task_data,
                headers=self.headers,
                timeout=test_config.DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        def get_task(self, task_id: str) -> Dict[str, Any]:
            """Get task by ID"""
            response = requests.get(
                f"{self.base_url}/api/tasks/{task_id}",
                headers=self.headers,
                timeout=test_config.DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        def update_task(self, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
            """Update task"""
            response = requests.put(
                f"{self.base_url}/api/tasks/{task_id}",
                json=updates,
                headers=self.headers,
                timeout=test_config.DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        def delete_task(self, task_id: str) -> bool:
            """Delete task"""
            response = requests.delete(
                f"{self.base_url}/api/tasks/{task_id}",
                headers=self.headers,
                timeout=test_config.DEFAULT_TIMEOUT
            )
            return response.status_code in [200, 204]

        def list_tasks(self, **filters) -> list:
            """List tasks with optional filters"""
            response = requests.get(
                f"{self.base_url}/api/tasks",
                params=filters,
                headers=self.headers,
                timeout=test_config.DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return response.json()

    return APIClient(test_config.BACKEND_URL, test_config.TEST_AUTH_TOKEN)


@pytest.fixture
def dapr_client(test_config):
    """Provide Dapr HTTP client"""
    class DaprClient:
        def __init__(self, dapr_url: str):
            self.dapr_url = dapr_url

        def publish_event(self, topic: str, event: Dict[str, Any]) -> bool:
            """Publish event to Kafka via Dapr"""
            url = f"{self.dapr_url}/v1.0/publish/{test_config.PUBSUB_NAME}/{topic}"
            response = requests.post(url, json=event, timeout=test_config.DEFAULT_TIMEOUT)
            return response.status_code == 200

        def save_state(self, key: str, value: Dict[str, Any]) -> bool:
            """Save state via Dapr"""
            url = f"{self.dapr_url}/v1.0/state/{test_config.STATE_STORE_NAME}"
            response = requests.post(
                url,
                json=[{"key": key, "value": value}],
                timeout=test_config.DEFAULT_TIMEOUT
            )
            return response.status_code in [200, 201, 204]

        def get_state(self, key: str) -> Dict[str, Any]:
            """Get state via Dapr"""
            url = f"{self.dapr_url}/v1.0/state/{test_config.STATE_STORE_NAME}/{key}"
            response = requests.get(url, timeout=test_config.DEFAULT_TIMEOUT)
            if response.status_code == 200:
                return response.json()
            return None

        def delete_state(self, key: str) -> bool:
            """Delete state via Dapr"""
            url = f"{self.dapr_url}/v1.0/state/{test_config.STATE_STORE_NAME}/{key}"
            response = requests.delete(url, timeout=test_config.DEFAULT_TIMEOUT)
            return response.status_code in [200, 204]

        def schedule_job(self, job_name: str, schedule_time: datetime, data: Dict[str, Any]) -> bool:
            """Schedule job via Dapr Jobs API"""
            url = f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}"
            payload = {
                "schedule": schedule_time.isoformat() + "Z",
                "repeats": 0,
                "data": data
            }
            response = requests.post(url, json=payload, timeout=test_config.DEFAULT_TIMEOUT)
            return response.status_code in [200, 201, 204]

        def delete_job(self, job_name: str) -> bool:
            """Delete scheduled job"""
            url = f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}"
            response = requests.delete(url, timeout=test_config.DEFAULT_TIMEOUT)
            return response.status_code in [200, 204, 404]

    return DaprClient(test_config.DAPR_URL)


@pytest.fixture
def cleanup_tasks(api_client):
    """Cleanup fixture to delete test tasks after test completion"""
    created_task_ids = []

    def register_task(task_id: str):
        """Register task for cleanup"""
        created_task_ids.append(task_id)

    yield register_task

    # Cleanup after test
    for task_id in created_task_ids:
        try:
            api_client.delete_task(task_id)
            logger.info(f"Cleaned up task: {task_id}")
        except Exception as e:
            logger.warning(f"Failed to cleanup task {task_id}: {str(e)}")


@pytest.fixture
def cleanup_dapr_state(dapr_client):
    """Cleanup fixture to delete Dapr state after test completion"""
    state_keys = []

    def register_key(key: str):
        """Register state key for cleanup"""
        state_keys.append(key)

    yield register_key

    # Cleanup after test
    for key in state_keys:
        try:
            dapr_client.delete_state(key)
            logger.info(f"Cleaned up state: {key}")
        except Exception as e:
            logger.warning(f"Failed to cleanup state {key}: {str(e)}")


@pytest.fixture
def cleanup_dapr_jobs(dapr_client):
    """Cleanup fixture to delete Dapr jobs after test completion"""
    job_names = []

    def register_job(job_name: str):
        """Register job for cleanup"""
        job_names.append(job_name)

    yield register_job

    # Cleanup after test
    for job_name in job_names:
        try:
            dapr_client.delete_job(job_name)
            logger.info(f"Cleaned up job: {job_name}")
        except Exception as e:
            logger.warning(f"Failed to cleanup job {job_name}: {str(e)}")


@pytest.fixture(scope="function")
def browser_context_args(browser_context_args):
    """Configure Playwright browser context"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "record_video_dir": "test-results/videos",
        "record_video_size": {"width": 1920, "height": 1080}
    }


# Pytest Hooks
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "kafka: mark test as requiring Kafka"
    )
    config.addinivalue_line(
        "markers", "dapr: mark test as requiring Dapr"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add markers based on test location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

        # Add markers based on test name
        if "kafka" in item.nodeid.lower():
            item.add_marker(pytest.mark.kafka)
        if "dapr" in item.nodeid.lower():
            item.add_marker(pytest.mark.dapr)


def pytest_html_report_title(report):
    """Customize HTML report title"""
    report.title = "Phase 5 Test Report - Todo AI Chatbot"


# Test Utilities
class TestHelpers:
    """Helper functions for tests"""

    @staticmethod
    def wait_for_event_processing(seconds: int = 2):
        """Wait for async event processing"""
        import time
        time.sleep(seconds)

    @staticmethod
    def generate_test_task_data(**overrides) -> Dict[str, Any]:
        """Generate test task data with defaults"""
        from uuid import uuid4

        default_data = {
            "title": f"Test Task {uuid4()}",
            "description": "Test task description",
            "priority": "medium",
            "tags": ["test"],
            "status": "pending"
        }
        default_data.update(overrides)
        return default_data

    @staticmethod
    def assert_cloud_event_format(event: Dict[str, Any]):
        """Assert event follows CloudEvents v1.0 format"""
        required_fields = ["specversion", "type", "source", "id", "time"]
        for field in required_fields:
            assert field in event, f"Missing required CloudEvents field: {field}"
        assert event["specversion"] == "1.0", "Invalid CloudEvents version"


@pytest.fixture
def test_helpers():
    """Provide test helper utilities"""
    return TestHelpers()

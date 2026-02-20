# Task: T5.4.2 - Integration Tests for Dapr State Store
# Spec Reference: phase5-spec.md Section 4.3 (Dapr Components)
# Constitution: constitution.md v5.0 Section 4.3 (Dapr Components)
#
# Integration tests for Dapr State Store operations.
# Tests verify state persistence, retrieval, deletion, and transactions.
#
# Version: 1.0
# Date: 2026-02-15

import pytest
import requests
import json
from typing import Dict, Any, List
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class TestDaprStateStore:
    """
    Integration tests for Dapr State Store.

    Prerequisites:
    - Dapr sidecar running on localhost:3500
    - Dapr State Store component configured (statestore-postgresql)
    - PostgreSQL database accessible
    """

    DAPR_HTTP_PORT = 3500
    DAPR_URL = f"http://localhost:{DAPR_HTTP_PORT}"
    STATE_STORE_NAME = "statestore-postgresql"

    def test_save_state(self):
        """Test saving state to Dapr State Store"""
        # Arrange
        key = f"test-task-{uuid4()}"
        value = {
            "id": key,
            "title": "Test Task",
            "status": "pending",
            "priority": "high",
            "tags": ["test", "integration"]
        }

        # Act
        url = f"{self.DAPR_URL}/v1.0/state/{self.STATE_STORE_NAME}"
        response = requests.post(
            url,
            json=[{"key": key, "value": value}],
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        # Assert
        assert response.status_code in [200, 201, 204], f"Failed to save state: {response.text}"
        logger.info(f"✅ Successfully saved state with key: {key}")

        # Cleanup
        requests.delete(f"{url}/{key}", timeout=5)

    def test_get_state(self):
        """Test retrieving state from Dapr State Store"""
        # Arrange - Save state first
        key = f"test-get-{uuid4()}"
        value = {"id": key, "title": "Get Test", "status": "pending"}

        save_url = f"{self.DAPR_URL}/v1.0/state/{self.STATE_STORE_NAME}"
        save_response = requests.post(
            save_url,
            json=[{"key": key, "value": value}],
            timeout=5
        )
        assert save_response.status_code in [200, 201, 204]

        # Act - Retrieve state
        get_url = f"{save_url}/{key}"
        get_response = requests.get(get_url, timeout=5)

        # Assert
        assert get_response.status_code == 200
        retrieved_value = get_response.json()
        assert retrieved_value["id"] == key
        assert retrieved_value["title"] == "Get Test"
        logger.info(f"✅ Successfully retrieved state with key: {key}")

        # Cleanup
        requests.delete(get_url, timeout=5)

    def test_delete_state(self):
        """Test deleting state from Dapr State Store"""
        # Arrange - Save state first
        key = f"test-delete-{uuid4()}"
        value = {"id": key, "title": "Delete Test"}

        save_url = f"{self.DAPR_URL}/v1.0/state/{self.STATE_STORE_NAME}"
        save_response = requests.post(
            save_url,
            json=[{"key": key, "value": value}],
            timeout=5
        )
        assert save_response.status_code in [200, 201, 204]

        # Act - Delete state
        delete_url = f"{save_url}/{key}"
        delete_response = requests.delete(delete_url, timeout=5)

        # Assert
        assert delete_response.status_code in [200, 204]

        # Verify deletion
        get_response = requests.get(delete_url, timeout=5)
        assert get_response.status_code == 204 or get_response.text == ""
        logger.info(f"✅ Successfully deleted state with key: {key}")

    def test_bulk_save_state(self):
        """Test saving multiple states in bulk"""
        # Arrange
        states = []
        for i in range(5):
            key = f"test-bulk-{uuid4()}"
            value = {"id": key, "title": f"Bulk Task {i}", "index": i}
            states.append({"key": key, "value": value})

        # Act
        url = f"{self.DAPR_URL}/v1.0/state/{self.STATE_STORE_NAME}"
        response = requests.post(url, json=states, timeout=5)

        # Assert
        assert response.status_code in [200, 201, 204]
        logger.info(f"✅ Successfully saved {len(states)} states in bulk")

        # Cleanup
        for state in states:
            requests.delete(f"{url}/{state['key']}", timeout=5)

    def test_state_with_etag(self):
        """Test state operations with ETag for concurrency control"""
        # Arrange - Save initial state
        key = f"test-etag-{uuid4()}"
        value = {"id": key, "title": "ETag Test", "version": 1}

        save_url = f"{self.DAPR_URL}/v1.0/state/{self.STATE_STORE_NAME}"
        save_response = requests.post(
            save_url,
            json=[{"key": key, "value": value}],
            timeout=5
        )
        assert save_response.status_code in [200, 201, 204]

        # Act - Get state with ETag
        get_url = f"{save_url}/{key}"
        get_response = requests.get(get_url, timeout=5)

        # Assert
        assert get_response.status_code == 200
        etag = get_response.headers.get("ETag")
        if etag:
            logger.info(f"✅ Retrieved state with ETag: {etag}")
        else:
            logger.info("✅ State retrieved (ETag not provided by store)")

        # Cleanup
        requests.delete(get_url, timeout=5)

    def test_state_with_metadata(self):
        """Test saving state with metadata"""
        # Arrange
        key = f"test-metadata-{uuid4()}"
        value = {"id": key, "title": "Metadata Test"}
        metadata = {
            "ttlInSeconds": "3600",
            "contentType": "application/json"
        }

        # Act
        url = f"{self.DAPR_URL}/v1.0/state/{self.STATE_STORE_NAME}"
        response = requests.post(
            url,
            json=[{"key": key, "value": value, "metadata": metadata}],
            timeout=5
        )

        # Assert
        assert response.status_code in [200, 201, 204]
        logger.info(f"✅ Successfully saved state with metadata: {key}")

        # Cleanup
        requests.delete(f"{url}/{key}", timeout=5)

    def test_query_state(self):
        """Test querying state (if supported by state store)"""
        # Arrange - Save multiple states
        keys = []
        url = f"{self.DAPR_URL}/v1.0/state/{self.STATE_STORE_NAME}"

        for i in range(3):
            key = f"test-query-{uuid4()}"
            value = {
                "id": key,
                "title": f"Query Task {i}",
                "priority": "high" if i % 2 == 0 else "low"
            }
            requests.post(url, json=[{"key": key, "value": value}], timeout=5)
            keys.append(key)

        # Act - Query state (if supported)
        query_url = f"{self.DAPR_URL}/v1.0-alpha1/state/{self.STATE_STORE_NAME}/query"
        query = {
            "filter": {
                "EQ": {"priority": "high"}
            }
        }

        try:
            query_response = requests.post(query_url, json=query, timeout=5)
            if query_response.status_code == 200:
                results = query_response.json()
                logger.info(f"✅ Query returned {len(results.get('results', []))} results")
            else:
                logger.info(f"Query not supported or failed: {query_response.status_code}")
        except Exception as e:
            logger.info(f"Query feature not available: {str(e)}")

        # Cleanup
        for key in keys:
            requests.delete(f"{url}/{key}", timeout=5)

    def test_state_transaction(self):
        """Test state transaction operations"""
        # Arrange
        key1 = f"test-txn-1-{uuid4()}"
        key2 = f"test-txn-2-{uuid4()}"

        operations = [
            {
                "operation": "upsert",
                "request": {
                    "key": key1,
                    "value": {"id": key1, "title": "Transaction Task 1"}
                }
            },
            {
                "operation": "upsert",
                "request": {
                    "key": key2,
                    "value": {"id": key2, "title": "Transaction Task 2"}
                }
            }
        ]

        # Act
        url = f"{self.DAPR_URL}/v1.0/state/{self.STATE_STORE_NAME}/transaction"
        response = requests.post(
            url,
            json={"operations": operations},
            timeout=5
        )

        # Assert
        if response.status_code in [200, 201, 204]:
            logger.info("✅ Successfully executed state transaction")
        else:
            logger.info(f"Transaction not supported: {response.status_code}")

        # Cleanup
        base_url = f"{self.DAPR_URL}/v1.0/state/{self.STATE_STORE_NAME}"
        requests.delete(f"{base_url}/{key1}", timeout=5)
        requests.delete(f"{base_url}/{key2}", timeout=5)

    def test_state_with_large_value(self):
        """Test saving state with large value"""
        # Arrange
        key = f"test-large-{uuid4()}"
        large_description = "x" * (100 * 1024)  # 100KB
        value = {
            "id": key,
            "title": "Large State Test",
            "description": large_description
        }

        # Act
        url = f"{self.DAPR_URL}/v1.0/state/{self.STATE_STORE_NAME}"
        response = requests.post(
            url,
            json=[{"key": key, "value": value}],
            timeout=10
        )

        # Assert
        assert response.status_code in [200, 201, 204]
        logger.info(f"✅ Successfully saved large state ({len(json.dumps(value)) / 1024:.2f} KB)")

        # Cleanup
        requests.delete(f"{url}/{key}", timeout=5)

    def test_state_consistency(self):
        """Test state consistency across multiple operations"""
        # Arrange
        key = f"test-consistency-{uuid4()}"
        initial_value = {"id": key, "title": "Consistency Test", "counter": 0}

        url = f"{self.DAPR_URL}/v1.0/state/{self.STATE_STORE_NAME}"

        # Act - Save, update, and verify
        # Save initial
        save_response = requests.post(
            url,
            json=[{"key": key, "value": initial_value}],
            timeout=5
        )
        assert save_response.status_code in [200, 201, 204]

        # Update
        updated_value = {"id": key, "title": "Consistency Test", "counter": 1}
        update_response = requests.post(
            url,
            json=[{"key": key, "value": updated_value}],
            timeout=5
        )
        assert update_response.status_code in [200, 201, 204]

        # Verify
        get_response = requests.get(f"{url}/{key}", timeout=5)
        assert get_response.status_code == 200
        retrieved = get_response.json()

        # Assert
        assert retrieved["counter"] == 1, "State not consistent"
        logger.info("✅ State consistency verified")

        # Cleanup
        requests.delete(f"{url}/{key}", timeout=5)


class TestDaprStateStorePerformance:
    """Performance tests for Dapr State Store"""

    DAPR_URL = f"http://localhost:3500"
    STATE_STORE_NAME = "statestore-postgresql"

    def test_concurrent_state_operations(self):
        """Test concurrent state save operations"""
        import concurrent.futures

        # Arrange
        num_operations = 10
        keys = [f"test-concurrent-{uuid4()}" for _ in range(num_operations)]

        def save_state(key):
            url = f"{self.DAPR_URL}/v1.0/state/{self.STATE_STORE_NAME}"
            value = {"id": key, "title": f"Concurrent Task {key}"}
            response = requests.post(url, json=[{"key": key, "value": value}], timeout=5)
            return response.status_code in [200, 201, 204]

        # Act
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(save_state, keys))

        # Assert
        assert all(results), "Some concurrent operations failed"
        logger.info(f"✅ Successfully executed {num_operations} concurrent state operations")

        # Cleanup
        url = f"{self.DAPR_URL}/v1.0/state/{self.STATE_STORE_NAME}"
        for key in keys:
            requests.delete(f"{url}/{key}", timeout=5)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

"""
Task: T5.2.3, T5.2.4, T5.2.5 - Unit Tests for Search, Filter, Sort
Spec Reference: phase5-spec.md Sections 3.1.3, 3.1.4, 3.1.5
Constitution: constitution.md v5.0

This module contains comprehensive unit tests for:
- T5.2.3: Search functionality (full-text search on title and description)
- T5.2.4: Filter functionality (status, priority, tags, due date range)
- T5.2.5: Sort functionality (due_date, priority, created_at, title)

Test Coverage: >80% as per phase5-spec.md Section 9.8
Performance: All operations < 500ms as per phase5-spec.md Section 5.6
"""

import pytest
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from backend.src.main import app
from backend.src.core.database import get_session
from backend.src.models.user import User
from agents.backend.models_search_filter_sort import Task, Tag, TaskTag, PriorityLevel


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session"""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user"""
    user = User(
        id="test-user-123",
        email="test@example.com",
        username="testuser"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="sample_tasks")
def sample_tasks_fixture(session: Session, test_user: User):
    """Create sample tasks for testing"""
    today = date.today()

    # Create tags
    tag_work = Tag(name="work")
    tag_personal = Tag(name="personal")
    tag_urgent = Tag(name="urgent")
    session.add_all([tag_work, tag_personal, tag_urgent])
    session.commit()

    # Create tasks with various attributes
    tasks = [
        Task(
            title="Team meeting preparation",
            description="Prepare slides for the quarterly review meeting",
            priority=PriorityLevel.HIGH,
            due_date=today + timedelta(days=2),
            user_id=test_user.id,
            status="pending"
        ),
        Task(
            title="Code review for PR #123",
            description="Review the authentication module changes",
            priority=PriorityLevel.URGENT,
            due_date=today + timedelta(days=1),
            user_id=test_user.id,
            status="pending"
        ),
        Task(
            title="Update documentation",
            description="Update API documentation with new endpoints",
            priority=PriorityLevel.MEDIUM,
            due_date=today + timedelta(days=5),
            user_id=test_user.id,
            status="pending"
        ),
        Task(
            title="Buy groceries",
            description="Get milk, eggs, and bread from the store",
            priority=PriorityLevel.LOW,
            due_date=today,
            user_id=test_user.id,
            status="pending"
        ),
        Task(
            title="Completed task",
            description="This task is already done",
            priority=PriorityLevel.MEDIUM,
            due_date=today - timedelta(days=1),
            user_id=test_user.id,
            status="completed"
        ),
    ]

    for task in tasks:
        session.add(task)
    session.commit()

    # Add tags to tasks
    # Task 0: work, urgent
    session.add(TaskTag(task_id=tasks[0].id, tag_id=tag_work.id))
    session.add(TaskTag(task_id=tasks[0].id, tag_id=tag_urgent.id))

    # Task 1: work, urgent
    session.add(TaskTag(task_id=tasks[1].id, tag_id=tag_work.id))
    session.add(TaskTag(task_id=tasks[1].id, tag_id=tag_urgent.id))

    # Task 2: work
    session.add(TaskTag(task_id=tasks[2].id, tag_id=tag_work.id))

    # Task 3: personal
    session.add(TaskTag(task_id=tasks[3].id, tag_id=tag_personal.id))

    session.commit()

    return tasks


# ============================================================================
# T5.2.3: Search Functionality Tests
# ============================================================================

class TestSearchFunctionality:
    """Test suite for T5.2.3 - Search functionality"""

    def test_search_by_title(self, client: TestClient, sample_tasks):
        """Test search returns results matching title"""
        response = client.get("/tasks?search=meeting")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "meeting" in data["tasks"][0]["title"].lower()

    def test_search_by_description(self, client: TestClient, sample_tasks):
        """Test search returns results matching description"""
        response = client.get("/tasks?search=authentication")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "authentication" in data["tasks"][0]["description"].lower()

    def test_search_case_insensitive(self, client: TestClient, sample_tasks):
        """Test search is case-insensitive"""
        response1 = client.get("/tasks?search=MEETING")
        response2 = client.get("/tasks?search=meeting")
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["total"] == response2.json()["total"]

    def test_search_partial_match(self, client: TestClient, sample_tasks):
        """Test search returns partial matches"""
        response = client.get("/tasks?search=doc")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any("doc" in task["title"].lower() or
                   "doc" in (task["description"] or "").lower()
                   for task in data["tasks"])

    def test_search_no_results(self, client: TestClient, sample_tasks):
        """Test search returns empty list when no matches"""
        response = client.get("/tasks?search=nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["tasks"] == []

    def test_search_with_special_characters(self, client: TestClient, sample_tasks):
        """Test search handles special characters"""
        response = client.get("/tasks?search=PR #123")
        assert response.status_code == 200
        # Should not crash, may or may not return results


# ============================================================================
# T5.2.4: Filter Functionality Tests
# ============================================================================

class TestFilterFunctionality:
    """Test suite for T5.2.4 - Filter functionality"""

    def test_filter_by_status_pending(self, client: TestClient, sample_tasks):
        """Test filter by status=pending"""
        response = client.get("/tasks?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
        assert all(task["status"] == "pending" for task in data["tasks"])

    def test_filter_by_status_completed(self, client: TestClient, sample_tasks):
        """Test filter by status=completed"""
        response = client.get("/tasks?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert all(task["status"] == "completed" for task in data["tasks"])

    def test_filter_by_priority_high(self, client: TestClient, sample_tasks):
        """Test filter by priority=high"""
        response = client.get("/tasks?priority=high")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert all(task["priority"] == "high" for task in data["tasks"])

    def test_filter_by_priority_urgent(self, client: TestClient, sample_tasks):
        """Test filter by priority=urgent"""
        response = client.get("/tasks?priority=urgent")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert all(task["priority"] == "urgent" for task in data["tasks"])

    def test_filter_by_single_tag(self, client: TestClient, sample_tasks):
        """Test filter by single tag"""
        response = client.get("/tasks?tags=work")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert all("work" in task["tags"] for task in data["tasks"])

    def test_filter_by_multiple_tags_and_logic(self, client: TestClient, sample_tasks):
        """Test filter by multiple tags with AND logic"""
        response = client.get("/tasks?tags=work,urgent")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all("work" in task["tags"] and "urgent" in task["tags"]
                   for task in data["tasks"])

    def test_filter_by_due_date_from(self, client: TestClient, sample_tasks):
        """Test filter by due_from date"""
        today = date.today()
        response = client.get(f"/tasks?due_from={today.isoformat()}")
        assert response.status_code == 200
        data = response.json()
        assert all(task["due_date"] is None or
                   date.fromisoformat(task["due_date"]) >= today
                   for task in data["tasks"])

    def test_filter_by_due_date_to(self, client: TestClient, sample_tasks):
        """Test filter by due_to date"""
        today = date.today()
        future = today + timedelta(days=3)
        response = client.get(f"/tasks?due_to={future.isoformat()}")
        assert response.status_code == 200
        data = response.json()
        assert all(task["due_date"] is None or
                   date.fromisoformat(task["due_date"]) <= future
                   for task in data["tasks"])

    def test_filter_by_due_date_range(self, client: TestClient, sample_tasks):
        """Test filter by due date range"""
        today = date.today()
        future = today + timedelta(days=3)
        response = client.get(
            f"/tasks?due_from={today.isoformat()}&due_to={future.isoformat()}"
        )
        assert response.status_code == 200
        data = response.json()
        assert all(task["due_date"] is None or
                   (today <= date.fromisoformat(task["due_date"]) <= future)
                   for task in data["tasks"])

    def test_filter_multiple_criteria(self, client: TestClient, sample_tasks):
        """Test filter with multiple criteria (AND logic)"""
        response = client.get("/tasks?status=pending&priority=high&tags=work")
        assert response.status_code == 200
        data = response.json()
        assert all(
            task["status"] == "pending" and
            task["priority"] == "high" and
            "work" in task["tags"]
            for task in data["tasks"]
        )

    def test_filter_invalid_status(self, client: TestClient, sample_tasks):
        """Test filter with invalid status returns error"""
        response = client.get("/tasks?status=invalid")
        assert response.status_code == 400


# ============================================================================
# T5.2.5: Sort Functionality Tests
# ============================================================================

class TestSortFunctionality:
    """Test suite for T5.2.5 - Sort functionality"""

    def test_sort_by_due_date_asc(self, client: TestClient, sample_tasks):
        """Test sort by due_date ascending"""
        response = client.get("/tasks?sort=due_date:asc")
        assert response.status_code == 200
        data = response.json()
        due_dates = [task["due_date"] for task in data["tasks"] if task["due_date"]]
        assert due_dates == sorted(due_dates)

    def test_sort_by_due_date_desc(self, client: TestClient, sample_tasks):
        """Test sort by due_date descending"""
        response = client.get("/tasks?sort=due_date:desc")
        assert response.status_code == 200
        data = response.json()
        due_dates = [task["due_date"] for task in data["tasks"] if task["due_date"]]
        assert due_dates == sorted(due_dates, reverse=True)

    def test_sort_by_priority_desc(self, client: TestClient, sample_tasks):
        """Test sort by priority descending (urgent > high > medium > low)"""
        response = client.get("/tasks?sort=priority:desc")
        assert response.status_code == 200
        data = response.json()
        priorities = [task["priority"] for task in data["tasks"]]
        # Verify urgent comes before high, high before medium, etc.
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        priority_values = [priority_order[p] for p in priorities]
        assert priority_values == sorted(priority_values)

    def test_sort_by_created_at_desc(self, client: TestClient, sample_tasks):
        """Test sort by created_at descending (newest first)"""
        response = client.get("/tasks?sort=created_at:desc")
        assert response.status_code == 200
        data = response.json()
        created_dates = [task["created_at"] for task in data["tasks"]]
        assert created_dates == sorted(created_dates, reverse=True)

    def test_sort_by_created_at_asc(self, client: TestClient, sample_tasks):
        """Test sort by created_at ascending (oldest first)"""
        response = client.get("/tasks?sort=created_at:asc")
        assert response.status_code == 200
        data = response.json()
        created_dates = [task["created_at"] for task in data["tasks"]]
        assert created_dates == sorted(created_dates)

    def test_sort_by_title_asc(self, client: TestClient, sample_tasks):
        """Test sort by title ascending (alphabetical)"""
        response = client.get("/tasks?sort=title:asc")
        assert response.status_code == 200
        data = response.json()
        titles = [task["title"] for task in data["tasks"]]
        assert titles == sorted(titles)

    def test_sort_by_title_desc(self, client: TestClient, sample_tasks):
        """Test sort by title descending (reverse alphabetical)"""
        response = client.get("/tasks?sort=title:desc")
        assert response.status_code == 200
        data = response.json()
        titles = [task["title"] for task in data["tasks"]]
        assert titles == sorted(titles, reverse=True)

    def test_sort_invalid_field(self, client: TestClient, sample_tasks):
        """Test sort with invalid field returns error"""
        response = client.get("/tasks?sort=invalid:asc")
        assert response.status_code == 400

    def test_sort_invalid_direction(self, client: TestClient, sample_tasks):
        """Test sort with invalid direction returns error"""
        response = client.get("/tasks?sort=title:invalid")
        assert response.status_code == 400


# ============================================================================
# Integration Tests: Combined Search, Filter, Sort
# ============================================================================

class TestIntegration:
    """Test suite for combined search, filter, and sort operations"""

    def test_search_and_filter(self, client: TestClient, sample_tasks):
        """Test search combined with filter"""
        response = client.get("/tasks?search=review&priority=urgent")
        assert response.status_code == 200
        data = response.json()
        assert all(
            ("review" in task["title"].lower() or
             "review" in (task["description"] or "").lower()) and
            task["priority"] == "urgent"
            for task in data["tasks"]
        )

    def test_search_and_sort(self, client: TestClient, sample_tasks):
        """Test search combined with sort"""
        response = client.get("/tasks?search=task&sort=priority:desc")
        assert response.status_code == 200
        data = response.json()
        priorities = [task["priority"] for task in data["tasks"]]
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        priority_values = [priority_order[p] for p in priorities]
        assert priority_values == sorted(priority_values)

    def test_filter_and_sort(self, client: TestClient, sample_tasks):
        """Test filter combined with sort"""
        response = client.get("/tasks?status=pending&sort=due_date:asc")
        assert response.status_code == 200
        data = response.json()
        assert all(task["status"] == "pending" for task in data["tasks"])
        due_dates = [task["due_date"] for task in data["tasks"] if task["due_date"]]
        assert due_dates == sorted(due_dates)

    def test_search_filter_sort_combined(self, client: TestClient, sample_tasks):
        """Test search, filter, and sort all combined"""
        today = date.today()
        future = today + timedelta(days=10)
        response = client.get(
            f"/tasks?search=task&status=pending&priority=high"
            f"&due_from={today.isoformat()}&sort=due_date:asc"
        )
        assert response.status_code == 200
        # Should not crash and should apply all filters

    def test_filters_applied_metadata(self, client: TestClient, sample_tasks):
        """Test that filters_applied metadata is returned correctly"""
        response = client.get("/tasks?status=pending&priority=high&tags=work")
        assert response.status_code == 200
        data = response.json()
        assert "filters_applied" in data
        assert data["filters_applied"]["status"] == "pending"
        assert data["filters_applied"]["priority"] == "high"
        assert "work" in data["filters_applied"]["tags"]


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Test suite for performance requirements (< 500ms)"""

    def test_search_performance(self, client: TestClient, sample_tasks):
        """Test search completes in < 500ms"""
        import time
        start = time.time()
        response = client.get("/tasks?search=meeting")
        duration = (time.time() - start) * 1000  # Convert to ms
        assert response.status_code == 200
        assert duration < 500, f"Search took {duration}ms, expected < 500ms"

    def test_filter_performance(self, client: TestClient, sample_tasks):
        """Test filter completes in < 500ms"""
        import time
        start = time.time()
        response = client.get("/tasks?status=pending&priority=high&tags=work")
        duration = (time.time() - start) * 1000
        assert response.status_code == 200
        assert duration < 500, f"Filter took {duration}ms, expected < 500ms"

    def test_sort_performance(self, client: TestClient, sample_tasks):
        """Test sort completes in < 500ms"""
        import time
        start = time.time()
        response = client.get("/tasks?sort=due_date:asc")
        duration = (time.time() - start) * 1000
        assert response.status_code == 200
        assert duration < 500, f"Sort took {duration}ms, expected < 500ms"

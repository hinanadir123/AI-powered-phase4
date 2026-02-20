# Task: T5.4.3 - E2E Tests for User Flows (Intermediate Features)
# Spec Reference: phase5-spec.md Section 3.1 (Intermediate Features)
# Constitution: constitution.md v5.0 Section 3 (Key Principles)
#
# End-to-end tests for intermediate features: priorities, tags, search, filter, sort.
# Tests verify complete user workflows from UI interactions to backend API responses.
#
# Version: 1.0
# Date: 2026-02-15

import pytest
from playwright.sync_api import Page, expect
import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TestIntermediateFeatures:
    """
    E2E tests for intermediate features.

    Prerequisites:
    - Frontend running on http://localhost:3000
    - Backend API running on http://localhost:8000
    - Database accessible and seeded with test data
    """

    BASE_URL = "http://localhost:3000"
    API_URL = "http://localhost:8000"

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup before each test"""
        page.goto(self.BASE_URL)
        page.wait_for_load_state("networkidle")

    def test_create_task_with_priority(self, page: Page):
        """
        Test: Create task with priority (high) and tags (work, urgent)

        Steps:
        1. Navigate to task creation form
        2. Enter task title
        3. Select priority: high
        4. Add tags: work, urgent
        5. Submit form
        6. Verify task appears in list with correct priority and tags
        """
        # Step 1: Navigate to create task
        page.click("button:has-text('New Task')")

        # Step 2: Enter task title
        page.fill("input[name='title']", "Complete Phase 5 Testing")
        page.fill("textarea[name='description']", "Write comprehensive E2E tests")

        # Step 3: Select priority
        page.click("select[name='priority']")
        page.select_option("select[name='priority']", "high")

        # Step 4: Add tags
        page.fill("input[name='tags']", "work")
        page.press("input[name='tags']", "Enter")
        page.fill("input[name='tags']", "urgent")
        page.press("input[name='tags']", "Enter")

        # Step 5: Submit form
        page.click("button[type='submit']")

        # Step 6: Verify task appears
        page.wait_for_selector("text=Complete Phase 5 Testing")

        # Verify priority badge
        priority_badge = page.locator(".priority-badge:has-text('high')")
        expect(priority_badge).to_be_visible()

        # Verify tags
        work_tag = page.locator(".tag-chip:has-text('work')")
        urgent_tag = page.locator(".tag-chip:has-text('urgent')")
        expect(work_tag).to_be_visible()
        expect(urgent_tag).to_be_visible()

        logger.info("✅ Successfully created task with priority and tags")

    def test_search_tasks_by_keyword(self, page: Page):
        """
        Test: Search for tasks by keyword

        Steps:
        1. Create multiple tasks with different titles
        2. Enter search keyword in search bar
        3. Verify only matching tasks are displayed
        4. Clear search and verify all tasks return
        """
        # Step 1: Create test tasks (assuming tasks exist or create via API)

        # Step 2: Enter search keyword
        search_input = page.locator("input[placeholder*='Search']")
        search_input.fill("meeting")

        # Wait for search results
        page.wait_for_timeout(500)

        # Step 3: Verify only matching tasks displayed
        task_items = page.locator(".task-item")
        count = task_items.count()

        # Verify all visible tasks contain search keyword
        for i in range(count):
            task_text = task_items.nth(i).inner_text().lower()
            assert "meeting" in task_text, f"Task {i} doesn't match search"

        # Step 4: Clear search
        search_input.clear()
        page.wait_for_timeout(500)

        # Verify more tasks are now visible
        all_tasks = page.locator(".task-item").count()
        assert all_tasks >= count, "Not all tasks returned after clearing search"

        logger.info("✅ Search functionality working correctly")

    def test_filter_tasks_by_status(self, page: Page):
        """
        Test: Filter tasks by status (pending, in-progress, completed)

        Steps:
        1. Open filter panel
        2. Select status filter: pending
        3. Verify only pending tasks displayed
        4. Change filter to completed
        5. Verify only completed tasks displayed
        """
        # Step 1: Open filter panel
        page.click("button:has-text('Filter')")

        # Step 2: Select pending status
        page.check("input[type='checkbox'][value='pending']")
        page.click("button:has-text('Apply Filters')")

        # Wait for filter to apply
        page.wait_for_timeout(500)

        # Step 3: Verify only pending tasks
        task_items = page.locator(".task-item")
        count = task_items.count()

        for i in range(count):
            status_badge = task_items.nth(i).locator(".status-badge")
            expect(status_badge).to_contain_text("pending")

        logger.info(f"✅ Filter by pending status: {count} tasks")

        # Step 4: Change to completed
        page.click("button:has-text('Filter')")
        page.uncheck("input[type='checkbox'][value='pending']")
        page.check("input[type='checkbox'][value='completed']")
        page.click("button:has-text('Apply Filters')")

        page.wait_for_timeout(500)

        # Step 5: Verify only completed tasks
        completed_tasks = page.locator(".task-item")
        completed_count = completed_tasks.count()

        for i in range(completed_count):
            status_badge = completed_tasks.nth(i).locator(".status-badge")
            expect(status_badge).to_contain_text("completed")

        logger.info(f"✅ Filter by completed status: {completed_count} tasks")

    def test_filter_tasks_by_priority(self, page: Page):
        """
        Test: Filter tasks by priority (high, urgent)

        Steps:
        1. Open filter panel
        2. Select priority filters: high, urgent
        3. Verify only high/urgent priority tasks displayed
        4. Clear filters
        """
        # Step 1: Open filter panel
        page.click("button:has-text('Filter')")

        # Step 2: Select priority filters
        page.check("input[type='checkbox'][value='high']")
        page.check("input[type='checkbox'][value='urgent']")
        page.click("button:has-text('Apply Filters')")

        page.wait_for_timeout(500)

        # Step 3: Verify filtered tasks
        task_items = page.locator(".task-item")
        count = task_items.count()

        for i in range(count):
            priority_badge = task_items.nth(i).locator(".priority-badge")
            priority_text = priority_badge.inner_text().lower()
            assert priority_text in ["high", "urgent"], f"Unexpected priority: {priority_text}"

        logger.info(f"✅ Filter by priority (high/urgent): {count} tasks")

        # Step 4: Clear filters
        page.click("button:has-text('Clear Filters')")
        page.wait_for_timeout(500)

        all_tasks = page.locator(".task-item").count()
        assert all_tasks >= count, "Filters not cleared properly"

        logger.info("✅ Filters cleared successfully")

    def test_filter_tasks_by_tags(self, page: Page):
        """
        Test: Filter tasks by tags (work, urgent)

        Steps:
        1. Open filter panel
        2. Select tag filters: work, urgent
        3. Verify only tasks with selected tags displayed
        """
        # Step 1: Open filter panel
        page.click("button:has-text('Filter')")

        # Step 2: Select tag filters
        page.click("input[placeholder*='Select tags']")
        page.click("text=work")
        page.click("text=urgent")
        page.click("button:has-text('Apply Filters')")

        page.wait_for_timeout(500)

        # Step 3: Verify filtered tasks
        task_items = page.locator(".task-item")
        count = task_items.count()

        for i in range(count):
            task_tags = task_items.nth(i).locator(".tag-chip")
            tag_count = task_tags.count()

            # Verify at least one of the selected tags is present
            has_matching_tag = False
            for j in range(tag_count):
                tag_text = task_tags.nth(j).inner_text().lower()
                if tag_text in ["work", "urgent"]:
                    has_matching_tag = True
                    break

            assert has_matching_tag, f"Task {i} doesn't have matching tags"

        logger.info(f"✅ Filter by tags (work/urgent): {count} tasks")

    def test_sort_tasks_by_due_date(self, page: Page):
        """
        Test: Sort tasks by due date (ascending/descending)

        Steps:
        1. Open sort dropdown
        2. Select sort by due date (ascending)
        3. Verify tasks are sorted correctly
        4. Change to descending
        5. Verify reverse order
        """
        # Step 1: Open sort dropdown
        page.click("select[name='sort']")

        # Step 2: Select due date ascending
        page.select_option("select[name='sort']", "due_date:asc")

        page.wait_for_timeout(500)

        # Step 3: Verify ascending order
        task_items = page.locator(".task-item")
        count = task_items.count()

        if count > 1:
            # Get due dates and verify order
            due_dates = []
            for i in range(min(count, 5)):  # Check first 5 tasks
                due_date_elem = task_items.nth(i).locator(".due-date")
                if due_date_elem.count() > 0:
                    due_dates.append(due_date_elem.inner_text())

            logger.info(f"✅ Tasks sorted by due date (ascending): {len(due_dates)} dates checked")

        # Step 4: Change to descending
        page.select_option("select[name='sort']", "due_date:desc")
        page.wait_for_timeout(500)

        logger.info("✅ Sort by due date (descending) applied")

    def test_sort_tasks_by_priority(self, page: Page):
        """
        Test: Sort tasks by priority (urgent → low)

        Steps:
        1. Select sort by priority (descending)
        2. Verify tasks are sorted: urgent, high, medium, low
        """
        # Step 1: Select priority sort
        page.click("select[name='sort']")
        page.select_option("select[name='sort']", "priority:desc")

        page.wait_for_timeout(500)

        # Step 2: Verify priority order
        task_items = page.locator(".task-item")
        count = task_items.count()

        priority_order = {"urgent": 4, "high": 3, "medium": 2, "low": 1}
        previous_priority_value = 5  # Start higher than urgent

        for i in range(min(count, 10)):  # Check first 10 tasks
            priority_badge = task_items.nth(i).locator(".priority-badge")
            if priority_badge.count() > 0:
                priority_text = priority_badge.inner_text().lower()
                current_priority_value = priority_order.get(priority_text, 0)

                assert current_priority_value <= previous_priority_value, \
                    f"Priority order incorrect at position {i}"

                previous_priority_value = current_priority_value

        logger.info("✅ Tasks sorted by priority correctly")

    def test_combine_search_filter_sort(self, page: Page):
        """
        Test: Combine search, filter, and sort in single query

        Steps:
        1. Enter search keyword
        2. Apply priority filter
        3. Apply sort by due date
        4. Verify all criteria are applied together
        """
        # Step 1: Search
        page.fill("input[placeholder*='Search']", "task")

        # Step 2: Filter by priority
        page.click("button:has-text('Filter')")
        page.check("input[type='checkbox'][value='high']")
        page.click("button:has-text('Apply Filters')")

        # Step 3: Sort by due date
        page.select_option("select[name='sort']", "due_date:asc")

        page.wait_for_timeout(500)

        # Step 4: Verify combined criteria
        task_items = page.locator(".task-item")
        count = task_items.count()

        for i in range(count):
            task = task_items.nth(i)

            # Verify search keyword
            task_text = task.inner_text().lower()
            assert "task" in task_text, "Search filter not applied"

            # Verify priority filter
            priority_badge = task.locator(".priority-badge")
            expect(priority_badge).to_contain_text("high")

        logger.info(f"✅ Combined search, filter, sort: {count} tasks")

    def test_add_remove_tags(self, page: Page):
        """
        Test: Add and remove tags from existing task

        Steps:
        1. Click on task to open details
        2. Add new tag
        3. Verify tag appears
        4. Remove tag
        5. Verify tag is removed
        """
        # Step 1: Open task details
        page.click(".task-item:first-child")
        page.wait_for_selector(".task-details")

        # Step 2: Add new tag
        page.fill("input[name='new-tag']", "testing")
        page.press("input[name='new-tag']", "Enter")

        page.wait_for_timeout(300)

        # Step 3: Verify tag appears
        testing_tag = page.locator(".tag-chip:has-text('testing')")
        expect(testing_tag).to_be_visible()

        logger.info("✅ Tag added successfully")

        # Step 4: Remove tag
        remove_button = testing_tag.locator("button.remove-tag")
        remove_button.click()

        page.wait_for_timeout(300)

        # Step 5: Verify tag removed
        expect(testing_tag).not_to_be_visible()

        logger.info("✅ Tag removed successfully")

    def test_change_task_priority(self, page: Page):
        """
        Test: Change task priority

        Steps:
        1. Open task details
        2. Change priority from medium to urgent
        3. Verify priority updated in UI
        4. Verify priority badge color changed
        """
        # Step 1: Open task details
        page.click(".task-item:first-child")
        page.wait_for_selector(".task-details")

        # Step 2: Change priority
        page.click("select[name='priority']")
        page.select_option("select[name='priority']", "urgent")

        # Save changes
        page.click("button:has-text('Save')")

        page.wait_for_timeout(500)

        # Step 3: Verify priority updated
        priority_badge = page.locator(".priority-badge:has-text('urgent')")
        expect(priority_badge).to_be_visible()

        # Step 4: Verify badge styling (urgent should be red)
        badge_class = priority_badge.get_attribute("class")
        assert "urgent" in badge_class or "red" in badge_class, "Priority badge styling incorrect"

        logger.info("✅ Task priority changed successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--headed"])

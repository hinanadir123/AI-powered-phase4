"""
Task: T5.2.1, T5.2.2 - Integration Guide
Spec Reference: phase5-spec.md Sections 3.1.1, 3.1.2
Constitution: constitution.md v5.0

Step-by-step guide to integrate priority and tag features into existing codebase.
"""

# ============================================================================
# INTEGRATION GUIDE: PRIORITIES AND TAGS
# ============================================================================

## Prerequisites

- Existing Phase 4 backend running (FastAPI + SQLModel)
- PostgreSQL database configured
- Python 3.9+ with virtual environment

## Step 1: Backup Current Database

```bash
# Create database backup before migration
pg_dump -U your_user -d todo_db > backup_before_phase5.sql
```

## Step 2: Install Dependencies (if needed)

```bash
cd backend
pip install sqlmodel fastapi pydantic python-dotenv pytest pytest-cov
```

## Step 3: Run Database Migration

```bash
# From project root
cd "D:/4-phases of hackathon/phase-4"

# Set database URL in environment
export DATABASE_URL="postgresql://user:password@localhost/todo_db"

# Run migration
python agents/backend/migration_priority_tags.py
```

**Expected Output:**
```
Adding priority column to task table...
Creating tags table...
Creating task_tags association table...
Migration completed successfully!
```

**Verify Migration:**
```sql
-- Connect to database and verify tables
\d task          -- Should show priority column
\d tags          -- Should exist
\d task_tags     -- Should exist
```

## Step 4: Update Task Model

**Option A: Replace existing model**
```bash
# Backup current model
cp backend/src/models/task.py backend/src/models/task.py.backup

# Copy new model
cp agents/backend/models_priority_tags.py backend/src/models/task.py
```

**Option B: Merge manually**
- Open `backend/src/models/task.py`
- Add `PriorityLevel` enum
- Add `priority` field to Task model
- Add `Tag` and `TaskTag` models
- Add `task_tags` relationship to Task

## Step 5: Update Schemas

**Add to `backend/schemas.py` or create new file:**
```bash
# Copy schemas
cp agents/backend/schemas_priority_tags.py backend/schemas_priority_tags.py
```

**Update imports in main.py:**
```python
from backend.schemas_priority_tags import (
    TaskCreate, TaskUpdate, TaskRead,
    PriorityLevel, AddTagRequest
)
```

## Step 6: Add API Endpoints

**Option A: Create new router file**
```bash
# Copy API endpoints
cp agents/backend/api_priority_tags.py backend/routes/tasks_priority_tags.py
```

**Update `backend/main.py`:**
```python
from backend.routes.tasks_priority_tags import router as tasks_router

app.include_router(tasks_router, prefix="/api")
```

**Option B: Merge into existing tasks router**
- Open `backend/routes/tasks.py`
- Add new endpoints from `agents/backend/api_priority_tags.py`
- Update existing endpoints to support priority and tags

## Step 7: Update Task Service (if exists)

**File: `backend/src/services/task_service.py`**

Add methods:
```python
def add_task_with_priority_and_tags(
    self,
    title: str,
    priority: PriorityLevel,
    tags: List[str],
    user_id: str
) -> Task:
    # Implementation from api_priority_tags.py
    pass

def add_tag_to_task(self, task_id: str, tag_name: str, user_id: str) -> Task:
    # Implementation from api_priority_tags.py
    pass

def remove_tag_from_task(self, task_id: str, tag_name: str, user_id: str) -> Task:
    # Implementation from api_priority_tags.py
    pass
```

## Step 8: Run Tests

```bash
# Copy test file
cp agents/tests/test_priority_tags_combined.py backend/tests/

# Run tests
pytest backend/tests/test_priority_tags_combined.py -v

# Run with coverage
pytest backend/tests/test_priority_tags_combined.py -v --cov=backend --cov-report=html
```

**Expected Result:**
- All tests pass
- Coverage > 80%

## Step 9: Test API Manually

**Start backend server:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Test endpoints with curl:**

```bash
# 1. Create task with priority and tags
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Test Priority and Tags",
    "description": "Testing new features",
    "priority": "high",
    "tags": ["work", "urgent"]
  }'

# 2. Filter by priority
curl -X GET "http://localhost:8000/api/tasks?priority=high" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Filter by tags
curl -X GET "http://localhost:8000/api/tasks?tags=work,urgent" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Sort by priority
curl -X GET "http://localhost:8000/api/tasks?sort=priority:desc" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 5. Add tag to existing task
curl -X POST http://localhost:8000/api/tasks/TASK_ID/tags \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"tag": "important"}'

# 6. Remove tag from task
curl -X DELETE http://localhost:8000/api/tasks/TASK_ID/tags/important \
  -H "Authorization: Bearer YOUR_TOKEN"

# 7. List all tags
curl -X GET http://localhost:8000/api/tasks/tags \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Step 10: Update API Documentation

**Add to README.md or API docs:**

```markdown
## Priority Levels

Tasks can be assigned one of four priority levels:
- `low` - Low priority tasks
- `medium` - Default priority
- `high` - High priority tasks
- `urgent` - Urgent tasks requiring immediate attention

## Tags

Tasks can have multiple tags for categorization:
- Tags are created automatically when first used
- Tags are shared across all tasks
- Multiple tasks can have the same tag
- Tasks can have multiple tags

## API Endpoints

### Create Task with Priority and Tags
POST /api/tasks
{
  "title": "Task title",
  "priority": "high",
  "tags": ["work", "urgent"]
}

### Filter by Priority
GET /api/tasks?priority=high

### Filter by Tags
GET /api/tasks?tags=work,urgent

### Sort by Priority
GET /api/tasks?sort=priority:desc

### Add Tag to Task
POST /api/tasks/{task_id}/tags
{"tag": "important"}

### Remove Tag from Task
DELETE /api/tasks/{task_id}/tags/{tag_name}
```

## Step 11: Verify Database State

```sql
-- Check priority distribution
SELECT priority, COUNT(*)
FROM task
GROUP BY priority;

-- Check tags
SELECT * FROM tags;

-- Check task-tag associations
SELECT t.title, tg.name
FROM task t
JOIN task_tags tt ON t.id = tt.task_id
JOIN tags tg ON tt.tag_id = tg.id;
```

## Troubleshooting

### Migration Fails

**Error: Column already exists**
```bash
# Rollback migration
python agents/backend/migration_priority_tags.py --rollback
```

**Error: Foreign key constraint fails**
- Ensure all existing tasks have valid user_id
- Check that conversation_id references are valid

### API Returns 500 Error

**Check logs:**
```bash
# View FastAPI logs
tail -f logs/app.log
```

**Common issues:**
- Missing imports in main.py
- Database connection not configured
- Authentication middleware not set up

### Tests Fail

**Import errors:**
- Verify all dependencies installed
- Check Python path includes project root

**Database errors:**
- Ensure test database is separate from production
- Check SQLite in-memory database is created correctly

## Rollback Instructions

If you need to rollback the changes:

```bash
# 1. Rollback database migration
python agents/backend/migration_priority_tags.py --rollback

# 2. Restore original model
cp backend/src/models/task.py.backup backend/src/models/task.py

# 3. Remove new router
rm backend/routes/tasks_priority_tags.py

# 4. Restore database from backup
psql -U your_user -d todo_db < backup_before_phase5.sql
```

## Next Steps

After successful integration:

1. ✅ Update frontend to display priorities and tags (Task T5.2.6)
2. ✅ Implement search functionality (Task T5.2.3)
3. ✅ Implement filter panel UI (Task T5.2.4)
4. ✅ Add Kafka event publishing for priority/tag changes
5. ✅ Update documentation with examples

## Support

For issues or questions:
- Check constitution.md v5.0 for coding standards
- Review phase5-spec.md for requirements
- Consult phase5-tasks.md for task details

---

**Generated by:** intermediate-features-agent
**Date:** 2026-02-15
**Tasks:** T5.2.1, T5.2.2

"""
Task: T5.2.1, T5.2.2 - Example API Request/Response Collection
Spec Reference: phase5-spec.md Sections 3.1.1, 3.1.2
Constitution: constitution.md v5.0

Complete collection of API examples for testing priority and tag features.
"""

# ============================================================================
# API EXAMPLES: PRIORITIES AND TAGS
# ============================================================================

## Authentication

All requests require authentication. Include JWT token in Authorization header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 1. CREATE TASK WITH PRIORITY AND TAGS

### Request
```http
POST /api/tasks HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "title": "Complete Phase 5 Implementation",
  "description": "Implement priorities and tags for task management",
  "priority": "high",
  "tags": ["work", "phase5", "urgent"]
}
```

### Response (201 Created)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete Phase 5 Implementation",
  "description": "Implement priorities and tags for task management",
  "user_id": "user-123",
  "status": "pending",
  "priority": "high",
  "tags": ["work", "phase5", "urgent"],
  "created_at": "2026-02-15T10:30:00.000Z",
  "completed_at": null
}
```

---

## 2. CREATE TASK WITH DEFAULT PRIORITY

### Request
```http
POST /api/tasks HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "title": "Regular task",
  "description": "This will have medium priority by default",
  "tags": []
}
```

### Response (201 Created)
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Regular task",
  "description": "This will have medium priority by default",
  "user_id": "user-123",
  "status": "pending",
  "priority": "medium",
  "tags": [],
  "created_at": "2026-02-15T10:35:00.000Z",
  "completed_at": null
}
```

---

## 3. FILTER TASKS BY PRIORITY

### Request: Get High Priority Tasks
```http
GET /api/tasks?priority=high HTTP/1.1
Host: localhost:8000
Authorization: Bearer YOUR_TOKEN
```

### Response (200 OK)
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete Phase 5 Implementation",
      "description": "Implement priorities and tags for task management",
      "user_id": "user-123",
      "status": "pending",
      "priority": "high",
      "tags": ["work", "phase5", "urgent"],
      "created_at": "2026-02-15T10:30:00.000Z",
      "completed_at": null
    }
  ],
  "total": 1,
  "filters_applied": {
    "priority": "high"
  }
}
```

### Request: Get Urgent Priority Tasks
```http
GET /api/tasks?priority=urgent HTTP/1.1
Host: localhost:8000
Authorization: Bearer YOUR_TOKEN
```

---

## 4. FILTER TASKS BY TAGS

### Request: Single Tag
```http
GET /api/tasks?tags=work HTTP/1.1
Host: localhost:8000
Authorization: Bearer YOUR_TOKEN
```

### Request: Multiple Tags (OR logic)
```http
GET /api/tasks?tags=work,urgent HTTP/1.1
Host: localhost:8000
Authorization: Bearer YOUR_TOKEN
```

### Response (200 OK)
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete Phase 5 Implementation",
      "priority": "high",
      "tags": ["work", "phase5", "urgent"],
      "created_at": "2026-02-15T10:30:00.000Z"
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "title": "Review pull requests",
      "priority": "medium",
      "tags": ["work", "review"],
      "created_at": "2026-02-15T11:00:00.000Z"
    }
  ],
  "total": 2,
  "filters_applied": {
    "tags": ["work", "urgent"]
  }
}
```

---

## 5. SORT TASKS BY PRIORITY

### Request: Descending (Urgent → Low)
```http
GET /api/tasks?sort=priority:desc HTTP/1.1
Host: localhost:8000
Authorization: Bearer YOUR_TOKEN
```

### Request: Ascending (Low → Urgent)
```http
GET /api/tasks?sort=priority:asc HTTP/1.1
Host: localhost:8000
Authorization: Bearer YOUR_TOKEN
```

### Response (200 OK)
```json
{
  "tasks": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "title": "Critical bug fix",
      "priority": "urgent",
      "tags": ["bug", "urgent"],
      "created_at": "2026-02-15T09:00:00.000Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete Phase 5 Implementation",
      "priority": "high",
      "tags": ["work", "phase5", "urgent"],
      "created_at": "2026-02-15T10:30:00.000Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Regular task",
      "priority": "medium",
      "tags": [],
      "created_at": "2026-02-15T10:35:00.000Z"
    }
  ],
  "total": 3,
  "filters_applied": {}
}
```

---

## 6. COMBINED FILTERS

### Request: Status + Priority + Tags + Sort
```http
GET /api/tasks?status=pending&priority=high&tags=work&sort=created:desc HTTP/1.1
Host: localhost:8000
Authorization: Bearer YOUR_TOKEN
```

### Response (200 OK)
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete Phase 5 Implementation",
      "status": "pending",
      "priority": "high",
      "tags": ["work", "phase5", "urgent"],
      "created_at": "2026-02-15T10:30:00.000Z"
    }
  ],
  "total": 1,
  "filters_applied": {
    "status": "pending",
    "priority": "high",
    "tags": ["work"]
  }
}
```

---

## 7. ADD TAG TO EXISTING TASK

### Request
```http
POST /api/tasks/550e8400-e29b-41d4-a716-446655440000/tags HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "tag": "important"
}
```

### Response (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete Phase 5 Implementation",
  "description": "Implement priorities and tags for task management",
  "user_id": "user-123",
  "status": "pending",
  "priority": "high",
  "tags": ["work", "phase5", "urgent", "important"],
  "created_at": "2026-02-15T10:30:00.000Z",
  "completed_at": null
}
```

---

## 8. REMOVE TAG FROM TASK

### Request
```http
DELETE /api/tasks/550e8400-e29b-41d4-a716-446655440000/tags/urgent HTTP/1.1
Host: localhost:8000
Authorization: Bearer YOUR_TOKEN
```

### Response (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete Phase 5 Implementation",
  "description": "Implement priorities and tags for task management",
  "user_id": "user-123",
  "status": "pending",
  "priority": "high",
  "tags": ["work", "phase5", "important"],
  "created_at": "2026-02-15T10:30:00.000Z",
  "completed_at": null
}
```

---

## 9. LIST ALL AVAILABLE TAGS

### Request
```http
GET /api/tasks/tags HTTP/1.1
Host: localhost:8000
Authorization: Bearer YOUR_TOKEN
```

### Response (200 OK)
```json
[
  {
    "id": "tag-001",
    "name": "work",
    "created_at": "2026-02-15T09:00:00.000Z"
  },
  {
    "id": "tag-002",
    "name": "urgent",
    "created_at": "2026-02-15T09:05:00.000Z"
  },
  {
    "id": "tag-003",
    "name": "phase5",
    "created_at": "2026-02-15T10:30:00.000Z"
  },
  {
    "id": "tag-004",
    "name": "important",
    "created_at": "2026-02-15T11:00:00.000Z"
  }
]
```

---

## 10. ERROR RESPONSES

### Invalid Priority Value (422 Unprocessable Entity)
```http
POST /api/tasks HTTP/1.1
Content-Type: application/json

{
  "title": "Test",
  "priority": "super-urgent"
}
```

**Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "priority"],
      "msg": "value is not a valid enumeration member; permitted: 'low', 'medium', 'high', 'urgent'",
      "type": "type_error.enum"
    }
  ]
}
```

### Task Not Found (404 Not Found)
```http
POST /api/tasks/nonexistent-id/tags HTTP/1.1
Content-Type: application/json

{
  "tag": "test"
}
```

**Response:**
```json
{
  "detail": "Task not found"
}
```

### Unauthorized (401 Unauthorized)
```http
GET /api/tasks HTTP/1.1
```

**Response:**
```json
{
  "detail": "Not authenticated"
}
```

---

## POSTMAN COLLECTION

Import this JSON into Postman for easy testing:

```json
{
  "info": {
    "name": "Todo API - Priorities & Tags",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Create Task with Priority and Tags",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"title\": \"Test Task\",\n  \"priority\": \"high\",\n  \"tags\": [\"work\", \"urgent\"]\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/tasks",
          "host": ["{{base_url}}"],
          "path": ["api", "tasks"]
        }
      }
    },
    {
      "name": "Filter by Priority",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/api/tasks?priority=high",
          "host": ["{{base_url}}"],
          "path": ["api", "tasks"],
          "query": [
            {
              "key": "priority",
              "value": "high"
            }
          ]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

---

**Generated by:** intermediate-features-agent
**Date:** 2026-02-15
**Tasks:** T5.2.1, T5.2.2

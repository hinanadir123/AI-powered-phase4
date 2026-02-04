# API Contracts for Phase II Task CRUD Feature

## Task Management Endpoints

### GET /api/{user_id}/tasks
Query Parameters:
- status: "all" | "pending" | "completed" (default: "all")
- sort: "created" | "title" (default: "created")

Headers:
- Authorization: Bearer <jwt_token>

Response (200):
```
[
  {
    "id": 1,
    "user_id": "user-uuid-here",
    "title": "Sample task",
    "description": "Task description here",
    "completed": false,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  },
  ...
]
```
Response (401): { "detail": "Not authenticated" }
Response (403): { "detail": "Access denied" }

### POST /api/{user_id}/tasks
Headers:
- Authorization: Bearer <jwt_token>

Request:
```
{
  "title": "New task",
  "description": "Optional description"
}
```

Response (201):
```
{
  "id": 1,
  "user_id": "user-uuid-here",
  "title": "New task",
  "description": "Optional description",
  "completed": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```
Response (400): { "detail": "Validation error" }
Response (401): { "detail": "Not authenticated" }
Response (403): { "detail": "Access denied" }

### GET /api/{user_id}/tasks/{id}
Headers:
- Authorization: Bearer <jwt_token>

Response (200):
```
{
  "id": 1,
  "user_id": "user-uuid-here",
  "title": "Sample task",
  "description": "Task description here",
  "completed": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```
Response (401): { "detail": "Not authenticated" }
Response (403): { "detail": "Access denied" }
Response (404): { "detail": "Task not found" }

### PUT /api/{user_id}/tasks/{id}
Headers:
- Authorization: Bearer <jwt_token>

Request:
```
{
  "title": "Updated task",
  "description": "Updated description"
}
```

Response (200):
```
{
  "id": 1,
  "user_id": "user-uuid-here",
  "title": "Updated task",
  "description": "Updated description",
  "completed": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```
Response (400): { "detail": "Validation error" }
Response (401): { "detail": "Not authenticated" }
Response (403): { "detail": "Access denied" }
Response (404): { "detail": "Task not found" }

### DELETE /api/{user_id}/tasks/{id}
Headers:
- Authorization: Bearer <jwt_token>

Response (204): No content
Response (401): { "detail": "Not authenticated" }
Response (403): { "detail": "Access denied" }
Response (404): { "detail": "Task not found" }

### PATCH /api/{user_id}/tasks/{id}/complete
Headers:
- Authorization: Bearer <jwt_token>

Response (200):
```
{
  "id": 1,
  "user_id": "user-uuid-here",
  "title": "Sample task",
  "description": "Task description here",
  "completed": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```
Response (401): { "detail": "Not authenticated" }
Response (403): { "detail": "Access denied" }
Response (404): { "detail": "Task not found" }
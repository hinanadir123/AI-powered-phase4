# API Contract: MCP Tools for Task Management

## Overview
This document defines the API contracts for the MCP tools that handle task management operations.

## Tool: add_task

### Purpose
Creates a new task for the authenticated user.

### Input Schema
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "user_id": "string (required, UUID)"
}
```

### Output Schema
```json
{
  "success": "boolean",
  "task": {
    "id": "string (UUID)",
    "title": "string",
    "description": "string",
    "status": "string (pending)",
    "created_at": "string (ISO 8601 datetime)",
    "user_id": "string (UUID)"
  },
  "error": "string (optional)"
}
```

## Tool: list_tasks

### Purpose
Retrieves all tasks for the authenticated user, with optional filtering.

### Input Schema
```json
{
  "user_id": "string (required, UUID)",
  "status_filter": "string (optional, 'pending'|'completed'|'all', default: 'all')"
}
```

### Output Schema
```json
{
  "success": "boolean",
  "tasks": [
    {
      "id": "string (UUID)",
      "title": "string",
      "description": "string",
      "status": "string (pending|completed)",
      "created_at": "string (ISO 8601 datetime)",
      "completed_at": "string (ISO 8601 datetime, nullable)",
      "user_id": "string (UUID)"
    }
  ],
  "total_count": "integer",
  "error": "string (optional)"
}
```

## Tool: complete_task

### Purpose
Marks a specific task as completed.

### Input Schema
```json
{
  "task_id": "string (required, UUID)",
  "user_id": "string (required, UUID)"
}
```

### Output Schema
```json
{
  "success": "boolean",
  "task": {
    "id": "string (UUID)",
    "title": "string",
    "status": "string (completed)",
    "completed_at": "string (ISO 8601 datetime)"
  },
  "error": "string (optional)"
}
```

## Tool: delete_task

### Purpose
Deletes a specific task.

### Input Schema
```json
{
  "task_id": "string (required, UUID)",
  "user_id": "string (required, UUID)"
}
```

### Output Schema
```json
{
  "success": "boolean",
  "task_id": "string (UUID)",
  "message": "string",
  "error": "string (optional)"
}
```

## Tool: update_task

### Purpose
Updates the details of a specific task.

### Input Schema
```json
{
  "task_id": "string (required, UUID)",
  "user_id": "string (required, UUID)",
  "title": "string (optional, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "status": "string (optional, 'pending'|'completed')"
}
```

### Output Schema
```json
{
  "success": "boolean",
  "task": {
    "id": "string (UUID)",
    "title": "string",
    "description": "string",
    "status": "string (pending|completed)",
    "updated_at": "string (ISO 8601 datetime)"
  },
  "error": "string (optional)"
}
```

## Common Error Responses
All tools may return these common error responses:

### Unauthorized Access
```json
{
  "success": false,
  "error": "Unauthorized access to task",
  "error_code": "AUTH_001"
}
```

### Resource Not Found
```json
{
  "success": false,
  "error": "Task not found",
  "error_code": "RESOURCE_001"
}
```

### Validation Error
```json
{
  "success": false,
  "error": "Validation failed: {detailed_reason}",
  "error_code": "VALIDATION_001"
}
```

### Server Error
```json
{
  "success": false,
  "error": "Internal server error",
  "error_code": "SERVER_001"
}
```

## Authorization
- All tools require the user_id to match the authenticated user
- Users can only operate on their own tasks
- Proper authentication and authorization checks must be performed before executing any tool
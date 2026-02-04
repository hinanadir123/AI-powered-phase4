# API Contract: Chat Endpoint

## Overview
This document defines the API contract for the chat endpoint that handles conversational interactions with the AI assistant.

## Endpoint
`POST /api/{user_id}/chat`

## Purpose
Processes natural language input from the user and returns AI-generated responses that may include task operations performed via MCP tools.

## Request

### Path Parameters
- `user_id` (string, required): The UUID of the authenticated user

### Headers
- `Authorization` (string, required): Bearer token in format "Bearer {jwt_token}"
- `Content-Type` (string, required): "application/json"

### Body
```json
{
  "message": "string (required)",
  "conversation_id": "string (optional, UUID)"
}
```

#### Fields
- `message`: The natural language input from the user
- `conversation_id`: Optional ID of an existing conversation; if omitted, a new conversation will be created

## Response

### Success Response (200 OK)
```json
{
  "response": "string",
  "conversation_id": "string (UUID)",
  "tasks_updated": [
    {
      "id": "string (UUID)",
      "title": "string",
      "status": "string (pending|completed)",
      "operation": "string (created|updated|completed|deleted)"
    }
  ],
  "next_message_expected": "boolean"
}
```

#### Fields
- `response`: The AI-generated response to the user's message
- `conversation_id`: The ID of the conversation (existing or newly created)
- `tasks_updated`: Array of tasks affected by the user's request
- `next_message_expected`: Boolean indicating if the AI expects additional input for multi-step operations

### Error Responses

#### 400 Bad Request
```json
{
  "error": "string",
  "code": "string"
}
```

#### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "code": "AUTH_001"
}
```

#### 403 Forbidden
```json
{
  "error": "Forbidden",
  "code": "AUTH_002"
}
```

#### 404 Not Found
```json
{
  "error": "Not Found",
  "code": "RESOURCE_001"
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "code": "SERVER_001"
}
```

## Authorization
- Requires valid JWT token in Authorization header
- User ID in path parameter must match the user ID in the JWT token
- Users can only access their own chat endpoints

## Business Logic
1. Validate JWT token and ensure user_id matches token
2. Process user's natural language message through AI agent
3. AI agent maps intents to appropriate MCP tools
4. Execute MCP tools as needed (add_task, list_tasks, etc.)
5. Generate AI response based on tool results
6. Persist conversation and message in database
7. Return response with updated task information

## Validation
- Message must not be empty
- User must be authenticated
- User can only access their own chat endpoint
- Conversation ID (if provided) must exist and belong to the user
# Data Model: AI-Powered Conversational Todo Manager

## Overview
This document defines the data model for the AI-Powered Conversational Todo Manager, including entity definitions, relationships, and validation rules.

## Entities

### Task
Represents a user's to-do item with properties like title, description, status, and timestamps.

**Fields**:
- `id` (UUID): Unique identifier for the task
- `title` (String, 1-200 chars): Title of the task
- `description` (String, max 1000 chars): Detailed description of the task
- `status` (Enum: pending/completed): Current status of the task
- `created_at` (DateTime): Timestamp when the task was created
- `completed_at` (DateTime, nullable): Timestamp when the task was completed
- `user_id` (UUID): Reference to the user who owns the task
- `conversation_id` (UUID, nullable): Reference to the conversation that created this task

**Validation Rules**:
- Title must be 1-200 characters
- Description must be max 1000 characters
- Status must be either 'pending' or 'completed'
- User ID must reference an existing user
- Cannot be completed before it was created

**State Transitions**:
- `pending` → `completed` (when task is marked as complete)
- No reverse transition allowed (completed tasks stay completed)

### Conversation
Represents a session of interaction between a user and the AI assistant, containing metadata like start/end times and associated user.

**Fields**:
- `id` (UUID): Unique identifier for the conversation
- `title` (String, nullable): Auto-generated or user-provided title for the conversation
- `created_at` (DateTime): Timestamp when the conversation started
- `updated_at` (DateTime): Timestamp when the conversation was last updated
- `user_id` (UUID): Reference to the user who owns the conversation

**Validation Rules**:
- User ID must reference an existing user
- Updated timestamp must be >= created timestamp

### Message
Represents an individual exchange within a conversation, including sender (user/AI), timestamp, and content.

**Fields**:
- `id` (UUID): Unique identifier for the message
- `content` (Text): The actual content of the message
- `sender_type` (Enum: user/ai): Indicates whether the message was sent by user or AI
- `timestamp` (DateTime): When the message was sent
- `conversation_id` (UUID): Reference to the conversation this message belongs to
- `user_id` (UUID): Reference to the user who initiated this conversation

**Validation Rules**:
- Content must not be empty
- Sender type must be either 'user' or 'ai'
- Conversation ID must reference an existing conversation
- User ID must match the user who owns the conversation

### User
Represents an authenticated user with unique identifier, authentication tokens, and associations to their tasks and conversations.

**Fields**:
- `id` (UUID): Unique identifier for the user
- `email` (String): User's email address
- `name` (String): User's display name
- `created_at` (DateTime): When the user account was created
- `updated_at` (DateTime): When the user account was last updated
- `auth_provider` (String): Authentication provider (e.g., 'better-auth')
- `auth_provider_user_id` (String): User ID from the authentication provider

**Validation Rules**:
- Email must be a valid email format
- Name must be 1-100 characters
- Email must be unique across all users

## Relationships

### Task Relationships
- **Belongs to** one User (many tasks per user)
- **Belongs to** one Conversation (optional, many tasks per conversation)

### Conversation Relationships
- **Belongs to** one User (many conversations per user)
- **Has many** Messages
- **Has many** Tasks (optional)

### Message Relationships
- **Belongs to** one Conversation (many messages per conversation)
- **Belongs to** one User (the user who initiated the conversation)

### User Relationships
- **Has many** Tasks
- **Has many** Conversations
- **Has many** Messages (through conversations)

## Database Constraints

### Indexes
- Index on `tasks.user_id` for efficient user-specific queries
- Index on `conversations.user_id` for efficient user-specific queries
- Index on `messages.conversation_id` for efficient conversation-specific queries
- Index on `tasks.status` for efficient filtering by status

### Foreign Key Constraints
- `tasks.user_id` references `users.id`
- `tasks.conversation_id` references `conversations.id` (nullable)
- `conversations.user_id` references `users.id`
- `messages.conversation_id` references `conversations.id`
- `messages.user_id` references `users.id`

## Access Control
- Users can only access their own tasks, conversations, and messages
- Backend must verify JWT token matches the requested user ID for all operations
- No cross-user access is permitted
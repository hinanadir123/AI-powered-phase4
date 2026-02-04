# Data Model for Phase II Todo Web App

## User Entity
- **Name**: User
- **Fields**:
  - id: string (primary key, managed by Better Auth)
  - email: string (unique, required)
  - name: string (required)
  - created_at: timestamp (required, default now)

## Task Entity
- **Name**: Task
- **Fields**:
  - id: int (primary key, auto-incrementing)
  - user_id: string (foreign key → users.id, required)
  - title: string (required, max 200 characters)
  - description: text (optional, nullable)
  - completed: bool (required, default False)
  - created_at: timestamp (required, default now)
  - updated_at: timestamp (required, updates on modification)

## Relationships
- Task entity has a many-to-one relationship with User (many tasks belong to one user)
- Foreign key constraint ensures referential integrity between tasks and users

## Validation Rules
- User.email: Must be a valid email format and unique across all users
- Task.title: Required field, must be between 1 and 200 characters inclusive
- Task.description: Optional field, if provided can be any length up to database text limit
- Task.completed: Boolean value, defaults to False when creating a new task
- Task.user_id: Must reference an existing user in the users table

## Indexes
- Index on tasks.user_id for efficient querying of user-specific tasks
- Index on tasks.completed for efficient filtering by completion status
- Composite index on (user_id, completed) for efficient filtering and sorting
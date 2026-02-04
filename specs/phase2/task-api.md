# Feature: Task Management API

## User Stories
- As a user, I want to authenticate so that I can securely access my tasks
- As an authenticated user, I want to create tasks with a title and optional description so that I can keep track of my to-dos
- As an authenticated user, I want to view all my tasks so that I can see what needs to be done
- As an authenticated user, I want to update existing tasks so that I can modify their details as needed
- As an authenticated user, I want to delete tasks that are no longer needed so that I can keep my list clean
- As an authenticated user, I want to mark tasks as complete so that I can track my progress
- As an authenticated user, I want to filter and sort my tasks so that I can organize them efficiently
- As a user, I want clear error messages when I enter invalid input so that I know how to correct my mistakes

## Acceptance Criteria

### Authentication
- System provides login and registration endpoints
- System generates JWT tokens upon successful authentication
- System verifies JWT tokens on all protected endpoints
- System returns 401 Unauthorized for invalid/missing tokens

### Create Task
- System accepts a task title (required, 1-200 characters)
- System accepts an optional task description (max 1000 characters)
- System assigns an auto-incrementing ID to each new task
- System associates the task with the authenticated user
- System sets the completed status to False by default
- System validates input length and provides error messages for invalid input
- System confirms successful addition of the task with 201 Created

### View Tasks
- System retrieves all tasks belonging to the authenticated user
- System filters tasks by status if specified (all, pending, completed)
- System sorts tasks by specified criteria (created, title)
- System returns tasks with ID, title, description, and completion status
- System returns empty array when no tasks exist
- System displays completion status as boolean

### View Single Task
- System retrieves a specific task by ID
- System verifies the task belongs to the authenticated user
- System returns task with ID, title, description, and completion status
- System returns 404 Not Found for non-existent tasks
- System returns 403 Forbidden if task doesn't belong to user

### Update Task
- System allows updating title and/or description of an existing task by ID
- System verifies the task belongs to the authenticated user
- System validates updated input length and provides error messages for invalid input
- System confirms successful update of the task with 200 OK
- System returns 404 Not Found for non-existent tasks
- System returns 403 Forbidden if task doesn't belong to user

### Delete Task
- System removes a task by ID
- System verifies the task belongs to the authenticated user
- System confirms successful deletion with 204 No Content
- System returns 404 Not Found for non-existent tasks
- System returns 403 Forbidden if task doesn't belong to user

### Toggle Complete
- System toggles the completion status of a task by ID
- System verifies the task belongs to the authenticated user
- System confirms successful status update with 200 OK
- System returns 404 Not Found for non-existent tasks
- System returns 403 Forbidden if task doesn't belong to user

## High-level Notes
- API endpoints follow the pattern: /api/{user_id}/tasks with all methods supporting proper HTTP verbs
- Authentication is handled via JWT tokens in Authorization header: "Authorization: Bearer <token>"
- Database uses Neon Serverless PostgreSQL with SQLModel for ORM
- User ID in the URL path must match the user ID in the JWT token for security
- All database operations should be wrapped in transactions where appropriate
- Error responses follow a consistent format: { "detail": "error message" }
# Feature: Task CRUD Operations

## User Stories
- As a user, I want to add tasks with a title and optional description so that I can keep track of my to-dos
- As a user, I want to view all my tasks in a list so that I can see what needs to be done
- As a user, I want to update existing tasks so that I can modify their details as needed
- As a user, I want to delete tasks that are no longer needed so that I can keep my list clean
- As a user, I want to mark tasks as complete so that I can track my progress
- As a user, I want clear error messages when I enter invalid input so that I know how to correct my mistakes

## Acceptance Criteria

### Add Task
- System accepts a task title (required, 1-200 characters)
- System accepts an optional task description (max 1000 characters)
- System assigns an auto-incrementing ID to each new task
- System sets the completed status to False by default
- System validates input length and provides error messages for invalid input
- System confirms successful addition of the task

### View Tasks
- System displays all tasks with ID, title, description, and completion status
- System shows "No tasks found" when the list is empty
- System displays completion status as "Yes" or "No"
- System presents tasks in a readable format

### Update Task
- System allows updating title and/or description of an existing task by ID
- System validates updated input length and provides error messages for invalid input
- System confirms successful update of the task
- System handles cases where the specified task ID does not exist

### Delete Task
- System removes a task by ID with confirmation prompt
- System handles cases where the specified task ID does not exist
- System confirms successful deletion of the task

### Mark Complete
- System toggles the completion status of a task by ID
- System handles cases where the specified task ID does not exist
- System confirms successful status update

## High-level Notes
- The application will use a console menu loop with numbered options (1: Add, 2: View, 3: Update, 4: Delete, 5: Mark, 0: Exit)
- Tasks will be stored as dictionaries in a list: {'id': int, 'title': str, 'desc': str, 'completed': bool}
- All storage is in-memory only, meaning data will be lost when the application exits
- The application will use only Python's built-in modules with no external dependencies
- Input validation will be implemented to ensure data integrity and provide user feedback
- Error handling will be comprehensive to manage invalid inputs and edge cases
#!/usr/bin/env python3
"""
Todo Console Application
A command-line todo application with in-memory storage that allows users to
add, view, update, delete, and mark tasks as complete through a console interface.
"""

# T003: Initialize global task list and ID counter in src/todo_app.py
tasks = []  # List to store task dictionaries
next_id = 1  # Counter for auto-incrementing IDs


def validate_title(title):
    """
    Validates the title length (1-200 characters).
    
    Args:
        title (str): The title to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    # T008: Implement input validation for title (1-200 chars) in add_task() function
    if len(title) < 1 or len(title) > 200:
        return False, f"Title must be between 1 and 200 characters. Current length: {len(title)}"
    return True, ""


def validate_description(desc):
    """
    Validates the description length (max 1000 characters).
    
    Args:
        desc (str): The description to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    # T009: Implement input validation for description (max 1000 chars) in add_task() function
    if len(desc) > 1000:
        return False, f"Description must be 1000 characters or less. Current length: {len(desc)}"
    return True, ""


def get_task_by_id(task_id):
    """
    Retrieves a task by its ID.
    
    Args:
        task_id (int): The ID of the task to retrieve
        
    Returns:
        dict: The task dictionary if found, None otherwise
    """
    for task in tasks:
        if task['id'] == task_id:
            return task
    return None


def add_task():
    """
    Adds a new task to the task list.
    T007: Create add_task() function that prompts for title and description in src/todo_app.py
    T010: Implement auto-incrementing ID assignment in add_task() function
    T011: Set completed status to False by default in add_task() function
    T012: Add new task to global task list in add_task() function
    T013: Add confirmation message for successful task addition in add_task() function
    """
    global next_id
    
    print("\n--- Add New Task ---")
    
    # Get title from user
    title = input("Enter task title (1-200 characters): ").strip()
    
    # Validate title
    is_valid, error_msg = validate_title(title)
    if not is_valid:
        print(f"Error: {error_msg}")
        return
    
    # Get description from user (optional)
    desc = input("Enter task description (optional, max 1000 characters): ").strip()
    
    # Validate description
    is_valid, error_msg = validate_description(desc)
    if not is_valid:
        print(f"Error: {error_msg}")
        return
    
    # Create new task
    new_task = {
        'id': next_id,
        'title': title,
        'desc': desc,
        'completed': False
    }
    
    # Add task to list
    tasks.append(new_task)
    
    # Increment ID counter
    next_id += 1
    
    # Confirm addition
    print(f"Task added successfully with ID {new_task['id']}!")


def view_tasks():
    """
    Displays all tasks in the task list.
    T015: Create view_tasks() function in src/todo_app.py
    T016: Implement check for empty task list in view_tasks() function
    T017: Display "No tasks found" when list is empty in view_tasks() function
    T018: Display all tasks with ID, title, description, and completion status in view_tasks() function
    T019: Format completion status as "Yes" or "No" in view_tasks() function
    """
    print("\n--- Task List ---")
    
    # T016: Implement check for empty task list in view_tasks() function
    # T017: Display "No tasks found" when list is empty in view_tasks() function
    if not tasks:
        print("No tasks found")
        return
    
    # T018: Display all tasks with ID, title, description, and completion status in view_tasks() function
    for task in tasks:
        # T019: Format completion status as "Yes" or "No" in view_tasks() function
        status = "Yes" if task['completed'] else "No"
        print(f"ID: {task['id']}, Title: {task['title']}, Description: {task['desc']}, Completed: {status}")


def update_task():
    """
    Updates an existing task's title and/or description.
    T021: Create update_task() function in src/todo_app.py
    T022: Prompt user for task ID in update_task() function
    T023: Validate that the task exists in update_task() function
    T024: Prompt user for new title and/or description in update_task() function
    T025: Validate updated input lengths in update_task() function
    T026: Update the task in the list in update_task() function
    T027: Add confirmation message for successful update in update_task() function
    """
    print("\n--- Update Task ---")
    
    # T022: Prompt user for task ID in update_task() function
    try:
        task_id = int(input("Enter the ID of the task to update: "))
    except ValueError:
        # T044: Handle ValueError when converting user input to integers
        print("Error: Invalid ID format. Please enter a number.")
        return
    
    # T023: Validate that the task exists in update_task() function
    task = get_task_by_id(task_id)
    if not task:
        # T043: Handle invalid task IDs (non-existent) with clear error messages
        print(f"Error: Task with ID {task_id} not found.")
        return
    
    print(f"Current task: ID {task['id']}, Title: {task['title']}, Description: {task['desc']}")
    
    # T024: Prompt user for new title and/or description in update_task() function
    new_title = input(f"Enter new title (leave blank to keep '{task['title']}'): ").strip()
    if not new_title:
        new_title = task['title']
    
    new_desc = input(f"Enter new description (leave blank to keep '{task['desc']}'): ").strip()
    if not new_desc:
        new_desc = task['desc']
    
    # T025: Validate updated input lengths in update_task() function
    is_valid, error_msg = validate_title(new_title)
    if not is_valid:
        print(f"Error: {error_msg}")
        return
    
    is_valid, error_msg = validate_description(new_desc)
    if not is_valid:
        print(f"Error: {error_msg}")
        return
    
    # T026: Update the task in the list in update_task() function
    task['title'] = new_title
    task['desc'] = new_desc
    
    # T027: Add confirmation message for successful update in update_task() function
    print(f"Task with ID {task_id} updated successfully!")


def delete_task():
    """
    Deletes a task from the task list.
    T029: Create delete_task() function in src/todo_app.py
    T030: Prompt user for task ID in delete_task() function
    T031: Validate that the task exists in delete_task() function
    T032: Show confirmation prompt before deletion in delete_task() function
    T033: Remove task from the list if confirmed in delete_task() function
    T034: Add confirmation message for successful deletion in delete_task() function
    """
    print("\n--- Delete Task ---")
    
    # T030: Prompt user for task ID in delete_task() function
    try:
        task_id = int(input("Enter the ID of the task to delete: "))
    except ValueError:
        # T044: Handle ValueError when converting user input to integers
        print("Error: Invalid ID format. Please enter a number.")
        return
    
    # T031: Validate that the task exists in delete_task() function
    task = get_task_by_id(task_id)
    if not task:
        # T043: Handle invalid task IDs (non-existent) with clear error messages
        print(f"Error: Task with ID {task_id} not found.")
        return
    
    print(f"You are about to delete: ID {task['id']}, Title: {task['title']}, Description: {task['desc']}")
    
    # T032: Show confirmation prompt before deletion in delete_task() function
    confirm = input("Are you sure you want to delete this task? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        # T033: Remove task from the list if confirmed in delete_task() function
        tasks.remove(task)
        
        # T034: Add confirmation message for successful deletion in delete_task() function
        print(f"Task with ID {task_id} deleted successfully!")
    else:
        print("Deletion cancelled.")


def mark_complete():
    """
    Toggles the completion status of a task.
    T036: Create mark_complete() function in src/todo_app.py
    T037: Prompt user for task ID in mark_complete() function
    T038: Validate that the task exists in mark_complete() function
    T039: Toggle the completed status of the task in mark_complete() function
    T040: Add confirmation message for successful status update in mark_complete() function
    """
    print("\n--- Mark Task Complete/Incomplete ---")
    
    # T037: Prompt user for task ID in mark_complete() function
    try:
        task_id = int(input("Enter the ID of the task to mark: "))
    except ValueError:
        # T044: Handle ValueError when converting user input to integers
        print("Error: Invalid ID format. Please enter a number.")
        return
    
    # T038: Validate that the task exists in mark_complete() function
    task = get_task_by_id(task_id)
    if not task:
        # T043: Handle invalid task IDs (non-existent) with clear error messages
        print(f"Error: Task with ID {task_id} not found.")
        return
    
    # T039: Toggle the completed status of the task in mark_complete() function
    task['completed'] = not task['completed']
    
    status = "completed" if task['completed'] else "incomplete"
    
    # T040: Add confirmation message for successful status update in mark_complete() function
    print(f"Task with ID {task_id} marked as {status}!")


def display_menu():
    """
    Displays the main menu options.
    """
    print("\n--- Todo App Menu ---")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Complete/Incomplete")
    print("0. Exit")


def main():
    """
    Main function containing the menu loop.
    T004: Create main menu loop with options 0-5 in src/todo_app.py
    T014: Connect menu option 1 to add_task() function in main loop
    T020: Connect menu option 2 to view_tasks() function in main loop
    T028: Connect menu option 3 to update_task() function in main loop
    T035: Connect menu option 4 to delete_task() function in main loop
    T041: Connect menu option 5 to mark_complete() function in main loop
    T042: Implement validation for invalid menu selections in main loop
    """
    print("Welcome to the Todo Console App!")
    print("This app stores tasks in memory only - data will be lost when the app exits.")
    
    while True:
        display_menu()
        
        try:
            choice = input("\nEnter your choice (0-5): ").strip()
            
            # T042: Implement validation for invalid menu selections in main loop
            if choice == '0':
                print("Thank you for using the Todo Console App. Goodbye!")
                break
            elif choice == '1':
                # T014: Connect menu option 1 to add_task() function in main loop
                add_task()
            elif choice == '2':
                # T020: Connect menu option 2 to view_tasks() function in main loop
                view_tasks()
            elif choice == '3':
                # T028: Connect menu option 3 to update_task() function in main loop
                update_task()
            elif choice == '4':
                # T035: Connect menu option 4 to delete_task() function in main loop
                delete_task()
            elif choice == '5':
                # T041: Connect menu option 5 to mark_complete() function in main loop
                mark_complete()
            else:
                print("Invalid choice. Please enter a number between 0 and 5.")
        except KeyboardInterrupt:
            # T045: Ensure application doesn't crash on invalid input
            print("\n\nApplication interrupted. Exiting...")
            break
        except Exception as e:
            # T046: Add clear error messages for all error conditions
            print(f"An unexpected error occurred: {e}")
            # T045: Ensure application doesn't crash on invalid input
            print("Please try again.")


if __name__ == "__main__":
    main()
# Todo App Overview – Phase 1

## Purpose
This project implements a command-line todo application with in-memory storage as part of Hackathon II: The Evolution of Todo, Phase 1. The application provides basic task management functionality allowing users to add, view, update, delete, and mark tasks as complete through a console interface.

## Current Phase
Phase I – In-Memory Python Console App. This phase focuses on implementing core CRUD operations for tasks with in-memory storage, using only Python's built-in modules without external dependencies.

## Tech Stack
| Component | Technology | Reason |
|-----------|------------|---------|
| Language | Python 3.12+ | Primary development language |
| Package Manager | UV | Modern Python package management |
| Storage | In-memory list | Simple storage mechanism for Phase I |
| Libraries | Built-in modules only | No external dependencies |
| Interface | Console/menu-driven | Simple user interaction |

## Features
- Add Task: Create new tasks with required title and optional description
- View Task List: Display all tasks with ID, title, description, and completion status
- Update Task: Modify existing task title and/or description
- Delete Task: Remove tasks by ID with confirmation
- Mark as Complete: Toggle task completion status
- Input Validation: Validate task titles (1-200 chars) and descriptions (max 1000 chars)
- Error Handling: Handle invalid inputs and ID not found scenarios
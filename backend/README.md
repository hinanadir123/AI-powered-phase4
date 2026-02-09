# AI-Powered Conversational Todo Manager - Backend

This is the backend for the AI-Powered Conversational Todo Manager. It provides the API, AI agent, and MCP tools for managing tasks through natural language commands.

## Features

- FastAPI-based REST API with support for natural language processing
- MCP-first architecture with tools for task operations
- Natural language processing for task management commands
- AI agent for intent recognition and tool orchestration
- JWT-based authentication and user isolation
- PostgreSQL database with SQLAlchemy ORM

## Tech Stack

- Python 3.11+
- FastAPI for the web framework
- SQLModel for database modeling
- PostgreSQL for data storage
- OpenAI API for AI capabilities
- Official MCP SDK for tool integration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```env
DATABASE_URL="postgresql://username:password@localhost:5432/todo_db"
OPENAI_API_KEY="your-openai-api-key"
MCP_SERVER_URL="http://localhost:8000"
SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. Run database migrations:
```bash
python -m src.core.database init-db
```

4. Start the server:
```bash
uvicorn src.main:app --reload --port 8000
```

## API Endpoints

- `POST /api/{user_id}/chat` - Main chat endpoint for conversational task management
- `GET /api/{user_id}/tasks` - Retrieve user's tasks
- `POST /api/{user_id}/tasks` - Create a new task
- `PUT /api/{user_id}/tasks/{task_id}` - Update a task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete a task
- `POST /api/{user_id}/tasks/{task_id}/complete` - Mark task as completed
- `POST /auth/token` - User authentication

## Architecture

- `src/models/` - Data models (User, Task, Conversation, Message)
- `src/services/` - Business logic (TaskService, MCP tools)
- `src/api/` - API routes and middleware
- `src/core/` - Core utilities (database, config, security)
- `src/ai/` - AI agent implementation
- `src/utils/` - Utility functions

## MCP Tools

The backend implements MCP tools for task operations:
- `add_task` - Create a new task
- `list_tasks` - Retrieve tasks
- `complete_task` - Mark a task as completed
- `delete_task` - Delete a task
- `update_task` - Update task details

## AI Agent

The AI agent processes natural language input and maps user intents to appropriate MCP tools. It handles:
- Intent recognition (add, list, complete, delete, update tasks)
- Multi-step operations
- Context management
- Error handling and user feedback
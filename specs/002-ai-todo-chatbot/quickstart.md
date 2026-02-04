# Quickstart Guide: AI-Powered Conversational Todo Manager

## Overview
This guide provides a quick introduction to setting up and running the AI-Powered Conversational Todo Manager. This application allows users to manage tasks through natural language interactions with an AI assistant.

## Prerequisites
- Python 3.11+
- Node.js 18+ and npm/yarn
- Access to OpenAI API
- Access to MCP server
- PostgreSQL database (Neon Serverless recommended)

## Environment Setup

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```env
   DATABASE_URL="postgresql://username:password@host:port/database"
   OPENAI_API_KEY="your-openai-api-key"
   MCP_SERVER_URL="http://localhost:8000"  # or your MCP server URL
   BETTER_AUTH_SECRET="your-secret-key"
   NEXT_PUBLIC_BETTER_AUTH_URL="http://localhost:3000"
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install JavaScript dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Set up environment variables in `.env.local`:
   ```env
   NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"
   NEXT_PUBLIC_MCP_SERVER_URL="http://localhost:8000"
   NEXT_PUBLIC_OPENAI_API_KEY="your-openai-api-key"
   ```

## Running the Application

### Backend
1. Run database migrations:
   ```bash
   python -m src.core.database migrate
   ```

2. Start the backend server:
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

### Frontend
1. Start the frontend development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

2. Visit `http://localhost:3000` in your browser

## Using the Application

### Authentication
1. Register a new account or sign in with an existing account
2. The application uses Better Auth for authentication

### Conversational Task Management
1. Navigate to the chat interface
2. Interact with the AI assistant using natural language:
   - "Add a task: Buy groceries"
   - "What are my tasks?"
   - "Mark the grocery task as complete"
   - "Update my meeting time to 3 PM"

### MCP Tools Integration
The backend exposes the following MCP tools:
- `add_task`: Creates a new task
- `list_tasks`: Lists all tasks for the user
- `complete_task`: Marks a task as completed
- `delete_task`: Deletes a task
- `update_task`: Updates task details

## Development

### Backend Development
- Models are located in `src/models/`
- Services are in `src/services/`
- API routes are in `src/api/routes/`
- MCP tools are implemented in `src/services/mcp_tools.py`

### Frontend Development
- Components are in `src/components/`
- Pages are in `src/pages/`
- API services are in `src/services/`

## Testing
Run backend tests:
```bash
pytest
```

Run frontend tests:
```bash
npm run test
```

## Configuration Notes
- The application follows a stateless architecture with all state persisted in the database
- All API requests require JWT authentication
- Users can only access their own tasks and conversations
- The AI agent processes natural language and maps intents to appropriate MCP tools
# Todo AI Chatbot - Phase III: AI-Powered Conversational Todo Manager

Welcome to the Todo AI Chatbot project, Phase III - AI-Powered Conversational Todo Manager. This application allows users to manage their tasks through natural language conversations with an AI assistant.

## Overview

This project implements an AI-powered conversational interface for task management. Users can interact with the system using natural language to add, update, complete, and delete tasks. The system leverages MCP tools and OpenAI Agents SDK to interpret user intents and execute appropriate actions.

## Architecture

The application follows a microservice architecture with:

- **Frontend**: Next.js application with a chat interface built using Material UI
- **Backend**: FastAPI server with MCP tools for task operations
- **Database**: PostgreSQL database for persistent storage
- **AI Agent**: Natural language processing using OpenAI API
- **Authentication**: JWT-based authentication with user isolation

## Features

- Natural language task management (add, list, complete, delete, update)
- Conversational AI assistant
- Persistent conversation history
- Secure authentication and user isolation
- MCP-first architecture for standardized tool integration
- Responsive web interface

## Project Structure

```
├── backend/              # FastAPI backend server
│   ├── src/
│   │   ├── models/       # Data models (User, Task, Conversation, Message)
│   │   ├── services/     # Business logic (TaskService, MCP tools)
│   │   ├── api/          # API routes and middleware
│   │   ├── core/         # Core utilities (database, config, security)
│   │   ├── ai/           # AI agent implementation
│   │   └── utils/        # Utility functions
│   └── requirements.txt  # Python dependencies
├── frontend/             # Next.js frontend application
│   ├── app/              # Next.js 14 App Router pages
│   ├── src/
│   │   ├── components/   # UI components (ChatInterface, TaskList)
│   │   ├── services/     # API and authentication services
│   │   ├── types/        # TypeScript type definitions
│   │   └── utils/        # Utility functions
│   └── package.json      # Node.js dependencies
└── specs/                # Project specifications and plans
    └── 002-ai-todo-chatbot/
        ├── spec.md       # Feature specification
        ├── plan.md       # Implementation plan
        └── tasks.md      # Task breakdown
```

## Setup Instructions

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
DATABASE_URL="postgresql://username:password@localhost:5432/todo_db"
OPENAI_API_KEY="your-openai-api-key"
MCP_SERVER_URL="http://localhost:8000"
SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. Run database migrations:
```bash
python -m src.core.database init-db
```

5. Start the backend server:
```bash
uvicorn src.main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install JavaScript dependencies:
```bash
npm install
```

3. Set up environment variables in `.env.local`:
```env
NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"
NEXT_PUBLIC_CHAT_API_URL="http://localhost:8000/api"
```

4. Start the frontend development server:
```bash
npm run dev
```

Visit `http://localhost:3000` to access the application.

## Usage

1. Register a new account or sign in with an existing account
2. Navigate to the dashboard to access the chat interface
3. Interact with the AI assistant using natural language:
   - "Add a task: Buy groceries"
   - "What are my tasks?"
   - "Mark the grocery task as complete"
   - "Update my meeting time to 3 PM"

## Development

### Backend Development
- Models are located in `src/models/`
- Services are in `src/services/`
- API routes are in `src/api/routes/`
- AI agent logic is in `src/ai/agent.py`

### Frontend Development
- Pages are in `app/` (Next.js App Router)
- Components are in `src/components/`
- API services are in `src/services/`
- Type definitions are in `src/types/`

## Testing

Run backend tests:
```bash
pytest
```

Run frontend tests:
```bash
npm run test
```
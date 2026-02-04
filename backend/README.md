# Todo AI Chatbot - Backend

Backend for the AI-powered conversational todo manager. Built with FastAPI and Python.

## Features
- MCP tools for task management
- Natural language processing for task operations
- JWT-based authentication
- PostgreSQL database integration
- AI agent for intent recognition

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```env
DATABASE_URL="postgresql://username:password@host:port/database"
OPENAI_API_KEY="your-openai-api-key"
MCP_SERVER_URL="http://localhost:8000"
BETTER_AUTH_SECRET="your-secret-key"
NEXT_PUBLIC_BETTER_AUTH_URL="http://localhost:3000"
```

3. Run database migrations:
```bash
python -m src.core.database migrate
```

4. Start the server:
```bash
uvicorn src.main:app --reload --port 8000
```

## Endpoints
- `POST /api/{user_id}/chat` - Main chat endpoint for conversational task management
- `/auth` - Authentication endpoints
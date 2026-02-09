# AI-Powered Conversational Todo Manager - Frontend

This is the frontend for the AI-Powered Conversational Todo Manager. It provides a chat interface for managing tasks through natural language commands.

## Features

- Conversational task management interface using natural language
- Real-time chat with AI assistant
- Task listing and management
- User authentication and session handling
- Responsive design for desktop and mobile

## Tech Stack

- Next.js 14 (App Router)
- React 18
- TypeScript
- Material UI (MUI) for components
- Axios for API requests

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables in `.env.local`:
```env
NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"
NEXT_PUBLIC_CHAT_API_URL="http://localhost:8000/api"
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Project Structure

- `app/` - Next.js 14 App Router pages
- `src/components/` - Reusable UI components (ChatInterface, TaskList, etc.)
- `src/services/` - API and authentication services
- `src/types/` - TypeScript type definitions
- `src/utils/` - Utility functions

## Key Components

- `ChatInterface` - Main chat interface for conversational task management
- `TaskList` - Component for displaying and managing tasks
- `AuthContext` - Authentication context for user management

## API Integration

The frontend communicates with the backend API at the configured `NEXT_PUBLIC_BACKEND_URL`. Key endpoints include:

- `/api/{user_id}/chat` - Chat endpoint for conversational task management
- `/api/{user_id}/tasks` - Task management endpoints
- `/auth` - Authentication endpoints

## Running with the Backend

For full functionality, this frontend needs to run alongside the backend server. Make sure the backend is running on the configured port before starting the frontend.
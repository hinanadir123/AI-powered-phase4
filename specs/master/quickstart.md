# Quickstart Guide: Phase II - Full-Stack Todo Application

## Overview
This guide provides step-by-step instructions to get the full-stack todo application up and running with authentication and backend integration.

## Prerequisites
- Node.js 18+ installed
- Python 3.9+ installed
- Neon PostgreSQL account with database created
- Environment variables configured for both frontend and backend

## Setup Instructions

### 1. Clone and Navigate to Project
```bash
cd C:\Users\PARAS COMPUTER\OneDrive\Desktop\phase1-todo-console
```

### 2. Backend Setup
1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```env
DATABASE_URL=postgresql://neondb_owner:npg_h8CmXFGVRx3E@ep-green-recipe-ahu3fj11-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
BETTER_AUTH_SECRET=Hm7r69DwRY2ZJIJ9JV4PFa9w2UppH9az
BETTER_AUTH_URL=http://localhost:3000
```

4. Run the application:
```bash
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables in `.env.local`:
```env
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

## Running the Application
1. Start the backend server first (port 8000)
2. Start the frontend server in a separate terminal (port 3000)
3. Access the frontend application at http://localhost:3000
4. Register a new account or log in to begin using the application

## API Documentation
- Backend API documentation is available at http://localhost:8000/docs when running in development
- All API endpoints require authentication via JWT token in the Authorization header
- Use the format: `Authorization: Bearer <token>`

## Common Commands
- Start backend: `uvicorn main:app --reload --port 8000`
- Start frontend: `npm run dev`
- Install backend deps: `pip install -r requirements.txt`
- Install frontend deps: `npm install`

## Troubleshooting
- If you get database connection errors, verify your Neon PostgreSQL credentials
- If authentication isn't working, ensure the BETTER_AUTH_SECRET matches between frontend and backend
- If API calls fail, check that the NEXT_PUBLIC_BACKEND_API_URL is set correctly in frontend
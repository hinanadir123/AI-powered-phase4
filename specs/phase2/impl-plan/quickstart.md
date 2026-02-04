# Quickstart Guide for Phase II Full-Stack Todo Web App

## Prerequisites
- Node.js 18+ installed
- Python 3.9+ installed
- Neon PostgreSQL account with database created
- Environment variables configured for both frontend and backend

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt` (or use uv: `uv pip install -r requirements.txt`)
3. Set up environment variables in `.env`:
   ```
   DATABASE_URL=your_neon_postgres_connection_string
   JWT_SECRET_KEY=your_jwt_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
4. Run the application: `uvicorn main:app --reload`

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install` (or `pnpm install`)
3. Set up environment variables in `.env.local`:
   ```
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=your_nextauth_secret
   BACKEND_API_URL=http://localhost:8000
   ```
4. Run the development server: `npm run dev` (or `pnpm dev`)

## Running the Application
1. Start the backend server first
2. Start the frontend server in a separate terminal
3. Access the application at http://localhost:3000
4. Register a new account or log in to begin using the application

## API Documentation
- Backend API documentation is available at http://localhost:8000/docs when running in development
- All API endpoints require authentication via JWT token in the Authorization header
- Use the format: `Authorization: Bearer <token>`
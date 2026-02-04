from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database and create tables

    # Import here to avoid circular imports during startup
    try:
        from db import create_db_and_tables
        create_db_and_tables()
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
        print("Make sure your DATABASE_URL is correctly set in the .env file")
    yield

app = FastAPI(lifespan=lifespan, title="Todo Backend API", version="1.0.0")

# Add CORS middleware with proper configuration for credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# Include the task and auth routes
from routes.tasks import router as tasks_router
from routes.auth import router as auth_router

app.include_router(tasks_router)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Todo Backend API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
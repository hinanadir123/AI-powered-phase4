from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes.chat import router as chat_router
from .api.routes.auth import router as auth_router
from .core.config import settings
from .core.database import engine
from .models import user, task, conversation, message  # Import models to register them
from sqlmodel import SQLModel


# Create the FastAPI app
app = FastAPI(
    title="AI-Powered Conversational Todo Manager",
    description="Backend API for the AI-powered todo chatbot",
    version="1.0.0"
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(chat_router, prefix="/api")
app.include_router(auth_router, prefix="/auth")


@app.on_event("startup")
async def startup_event():
    """Initialize the database on startup."""
    # Create database tables
    SQLModel.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    """Root endpoint for health check."""
    return {"message": "AI-Powered Conversational Todo Manager Backend"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
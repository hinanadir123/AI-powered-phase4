from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TaskResponse(BaseModel):
    """Response model for task operations."""
    id: str
    title: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    user_id: str
    conversation_id: Optional[str] = None


class TaskListResponse(BaseModel):
    """Response model for listing tasks."""
    tasks: List[TaskResponse]
    total_count: int


class ConversationResponse(BaseModel):
    """Response model for conversation operations."""
    id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user_id: str


class MessageResponse(BaseModel):
    """Response model for message operations."""
    id: str
    content: str
    sender_type: str
    timestamp: datetime
    conversation_id: str
    user_id: str


class UserResponse(BaseModel):
    """Response model for user operations."""
    id: str
    email: str
    name: str
    created_at: datetime
    updated_at: datetime
    auth_provider: str
    auth_provider_user_id: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    conversation_id: str
    tasks_updated: List[dict]
    next_message_expected: bool


class ErrorResponse(BaseModel):
    """Response model for error responses."""
    error: str
    detail: str
    code: str


class SuccessResponse(BaseModel):
    """Generic success response model."""
    success: bool
    message: Optional[str] = None
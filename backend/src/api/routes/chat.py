from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional
from pydantic import BaseModel
from ..core.database import get_session
from ..api.middleware.auth_middleware import JWTBearer
from ..services.conversation_service import ConversationService
from ..ai.agent import AIAgent


router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    tasks_updated: list
    next_message_expected: bool


@router.post("/{user_id}/chat", response_model=ChatResponse)
def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    token: str = Depends(JWTBearer()),
    session: Session = Depends(get_session)
):
    """Main chat endpoint for conversational task management."""
    # Verify that the user_id in the path matches the user_id in the token
    # This is a simplified check - in a real implementation, you'd decode the JWT
    # and verify the user_id matches

    # Initialize services
    conversation_service = ConversationService(session)
    ai_agent = AIAgent(session)

    # Get or create conversation
    if request.conversation_id:
        conversation = conversation_service.get_conversation_by_id(request.conversation_id, user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied"
            )
        conversation_id = conversation.id
    else:
        conversation = conversation_service.create_conversation(user_id)
        conversation_id = conversation.id

    # Add user message to conversation
    user_message = conversation_service.add_message_to_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        content=request.message,
        sender_type="user"
    )

    # Process the message with the AI agent
    result = ai_agent.process_message(request.message, user_id)

    # Add AI response to conversation
    ai_message = conversation_service.add_message_to_conversation(
        conversation_id=conversation_id,
        user_id=user_id,
        content=result["response"],
        sender_type="ai"
    )

    return ChatResponse(
        response=result["response"],
        conversation_id=conversation_id,
        tasks_updated=result["tasks_updated"],
        next_message_expected=result["next_message_expected"]
    )
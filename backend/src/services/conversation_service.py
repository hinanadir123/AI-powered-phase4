from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from ..models.conversation import Conversation
from ..models.message import Message
from ..models.task import Task


class ConversationService:
    """Service class to handle conversation-related operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_conversation(self, user_id: str, title: Optional[str] = None) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            title=title,
            user_id=user_id
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation
    
    def get_conversation_by_id(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """Get a specific conversation by its ID and user ID."""
        query = select(Conversation).where(
            Conversation.id == conversation_id, 
            Conversation.user_id == user_id
        )
        conversation = self.session.exec(query).first()
        return conversation
    
    def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a specific user."""
        query = select(Conversation).where(Conversation.user_id == user_id)
        conversations = self.session.exec(query).all()
        return conversations
    
    def add_message_to_conversation(self, conversation_id: str, user_id: str, 
                                   content: str, sender_type: str) -> Message:
        """Add a message to a conversation."""
        message = Message(
            content=content,
            sender_type=sender_type,
            conversation_id=conversation_id,
            user_id=user_id
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message
    
    def get_messages_for_conversation(self, conversation_id: str, user_id: str) -> List[Message]:
        """Get all messages for a specific conversation."""
        # Verify the user has access to this conversation
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return []
        
        query = select(Message).where(Message.conversation_id == conversation_id)
        messages = self.session.exec(query).all()
        return messages
    
    def update_conversation_title(self, conversation_id: str, user_id: str, title: str) -> Optional[Conversation]:
        """Update the title of a conversation."""
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)
            self.session.commit()
            self.session.refresh(conversation)
        return conversation
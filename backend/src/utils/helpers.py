"""
Utility functions for the AI-Powered Conversational Todo Manager backend.
"""

import re
from typing import Optional


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    """
    # Remove potentially dangerous characters/sequences
    sanitized = re.sub(r'[<>"\';]', '', text)
    return sanitized.strip()


def extract_task_info_from_message(message: str) -> dict:
    """
    Extract task information from a natural language message.
    This is a simple implementation - a real system would use NLP.
    """
    # Look for common patterns in the message
    title = ""
    description = ""
    
    # If the message contains a colon, treat the part after as the title
    if ':' in message:
        parts = message.split(':', 1)
        if len(parts) > 1:
            title = parts[1].strip()
    # If the message contains a dash, treat the part after as the title
    elif '-' in message:
        parts = message.split('-', 1)
        if len(parts) > 1:
            title = parts[1].strip()
    # Otherwise, use the entire message as the title (after removing command words)
    else:
        # Remove common command words
        command_words = ["add", "create", "new", "task", "please", "can you"]
        words = message.split()
        filtered_words = [word for word in words if word.lower() not in command_words]
        title = " ".join(filtered_words).strip()
    
    return {
        "title": title,
        "description": description
    }


def validate_task_title(title: str) -> tuple[bool, Optional[str]]:
    """
    Validate a task title according to business rules.
    Returns (is_valid, error_message).
    """
    if not title or len(title.strip()) == 0:
        return False, "Task title cannot be empty"
    
    if len(title) > 200:
        return False, "Task title must be 200 characters or less"
    
    return True, None


def validate_task_description(description: str) -> tuple[bool, Optional[str]]:
    """
    Validate a task description according to business rules.
    Returns (is_valid, error_message).
    """
    if description and len(description) > 1000:
        return False, "Task description must be 1000 characters or less"
    
    return True, None


def format_task_status(status: str) -> str:
    """
    Format task status to ensure consistency.
    """
    status_lower = status.lower()
    if status_lower in ["pending", "in progress", "todo"]:
        return "pending"
    elif status_lower in ["completed", "done", "finished"]:
        return "completed"
    else:
        return status_lower  # Return as-is if it's a custom status
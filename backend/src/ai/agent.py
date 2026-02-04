from typing import Dict, Any, List, Optional
from ..services.mcp_tools import MCPTaskTools
from sqlmodel import Session


class AIAgent:
    """AI Agent to process natural language and map to MCP tools."""

    def __init__(self, session: Session):
        self.mcp_tools = MCPTaskTools(session)
        self.session = session

    def process_message(self, message: str, user_id: str) -> Dict[str, Any]:
        """
        Process a natural language message and return an appropriate response.
        This method analyzes the user's intent and calls the appropriate MCP tools.
        """
        # Normalize the message
        normalized_message = message.strip().lower()

        # Determine intent and call appropriate tools
        if self._is_add_task_intent(normalized_message):
            return self._handle_add_task(message, user_id)
        elif self._is_list_tasks_intent(normalized_message):
            return self._handle_list_tasks(user_id)
        elif self._is_complete_task_intent(normalized_message):
            return self._handle_complete_task(message, user_id)
        elif self._is_delete_task_intent(normalized_message):
            return self._handle_delete_task(message, user_id)
        elif self._is_update_task_intent(normalized_message):
            return self._handle_update_task(message, user_id)
        else:
            # Default response for unrecognized intents
            return {
                "response": f"I received your message: '{message}'. How can I help you with your tasks?",
                "tasks_updated": [],
                "next_message_expected": False
            }

    def _is_add_task_intent(self, message: str) -> bool:
        """Check if the message indicates an intent to add a task."""
        add_indicators = ["add", "create", "new task", "make task"]
        return any(indicator in message for indicator in add_indicators)

    def _is_list_tasks_intent(self, message: str) -> bool:
        """Check if the message indicates an intent to list tasks."""
        list_indicators = ["list", "show", "view", "my tasks", "what are"]
        return any(indicator in message for indicator in list_indicators)

    def _is_complete_task_intent(self, message: str) -> bool:
        """Check if the message indicates an intent to complete a task."""
        complete_indicators = ["complete", "done", "finish", "mark as done"]
        return any(indicator in message for indicator in complete_indicators)

    def _is_delete_task_intent(self, message: str) -> bool:
        """Check if the message indicates an intent to delete a task."""
        delete_indicators = ["delete", "remove", "get rid of"]
        return any(indicator in message for indicator in delete_indicators)

    def _is_update_task_intent(self, message: str) -> bool:
        """Check if the message indicates an intent to update a task."""
        update_indicators = ["update", "change", "modify", "edit"]
        return any(indicator in message for indicator in update_indicators)

    def _extract_task_title(self, message: str) -> str:
        """Extract task title from the message."""
        # Look for common patterns like "add task: title" or "create task - title"
        separators = [":", "-", ":", "to"]
        for sep in separators:
            if sep in message:
                parts = message.split(sep, 1)
                if len(parts) > 1:
                    return parts[1].strip()

        # If no separator found, return the whole message minus command words
        command_words = ["add", "create", "task", "please", "can you"]
        words = message.split()
        filtered_words = [word for word in words if word not in command_words]
        return " ".join(filtered_words).strip()

    def _extract_task_identifier(self, message: str) -> str:
        """
        Extract task identifier (title or partial title) from the message.
        This is a simplified implementation - a real system would use more sophisticated NLP.
        """
        # Remove common command words
        command_words = ["complete", "finish", "mark", "as", "done", "delete", "remove", "update", "change", "modify", "edit", "task", "the", "a", "an"]
        words = message.split()
        filtered_words = [word for word in words if word.lower() not in command_words]

        # Join the remaining words to form a partial title
        identifier = " ".join(filtered_words).strip()

        # If identifier is too short, return None
        if len(identifier) < 2:
            return None

        return identifier

    def _find_task_by_identifier(self, identifier: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a task by its identifier (title or partial title).
        This is a simplified implementation - a real system would use fuzzy matching.
        """
        # Get all tasks for the user
        result = self.mcp_tools.list_tasks(user_id=user_id)

        if not result["success"]:
            return None

        tasks = result["tasks"]

        # Look for exact matches first
        for task in tasks:
            if identifier.lower() in task["title"].lower():
                return task

        # If no exact match, return None
        return None

    def _handle_add_task(self, message: str, user_id: str) -> Dict[str, Any]:
        """Handle adding a new task."""
        title = self._extract_task_title(message)

        if not title:
            return {
                "response": "I couldn't understand what task you want to add. Please specify the task title.",
                "tasks_updated": [],
                "next_message_expected": True
            }

        result = self.mcp_tools.add_task(title=title, user_id=user_id)

        if result["success"]:
            task = result["task"]
            return {
                "response": f"I've added the task '{task['title']}' to your list.",
                "tasks_updated": [task],
                "next_message_expected": False
            }
        else:
            return {
                "response": f"Sorry, I couldn't add the task: {result['error']}",
                "tasks_updated": [],
                "next_message_expected": False
            }

    def _handle_list_tasks(self, user_id: str) -> Dict[str, Any]:
        """Handle listing tasks."""
        result = self.mcp_tools.list_tasks(user_id=user_id)

        if result["success"]:
            tasks = result["tasks"]
            if tasks:
                task_list = []
                for task in tasks[:5]:  # Limit to first 5 tasks for brevity
                    task_list.append(f"- {task['title']} ({task['status']})")

                if len(tasks) > 5:
                    response = f"You have {len(tasks)} tasks. Here are the first 5:\n" + "\n".join(task_list)
                    response += f"\nAnd {len(tasks) - 5} more tasks."
                else:
                    response = f"You have {len(tasks)} tasks:\n" + "\n".join(task_list)
            else:
                response = "You don't have any tasks at the moment."

            return {
                "response": response,
                "tasks_updated": [],
                "next_message_expected": False
            }
        else:
            return {
                "response": f"Sorry, I couldn't retrieve your tasks: {result['error']}",
                "tasks_updated": [],
                "next_message_expected": False
            }

    def _handle_complete_task(self, message: str, user_id: str) -> Dict[str, Any]:
        """Handle completing a task."""
        # Extract task identifier from the message
        identifier = self._extract_task_identifier(message)

        if not identifier:
            return {
                "response": "I couldn't identify which task to complete. Please specify the task title.",
                "tasks_updated": [],
                "next_message_expected": True
            }

        # Find the task by identifier
        task = self._find_task_by_identifier(identifier, user_id)

        if not task:
            return {
                "response": f"I couldn't find a task matching '{identifier}'. Please check the task name and try again.",
                "tasks_updated": [],
                "next_message_expected": True
            }

        # Complete the task
        result = self.mcp_tools.complete_task(task_id=task["id"], user_id=user_id)

        if result["success"]:
            completed_task = result["task"]
            return {
                "response": f"I've marked the task '{completed_task['title']}' as completed.",
                "tasks_updated": [completed_task],
                "next_message_expected": False
            }
        else:
            return {
                "response": f"Sorry, I couldn't complete the task: {result['error']}",
                "tasks_updated": [],
                "next_message_expected": False
            }

    def _handle_delete_task(self, message: str, user_id: str) -> Dict[str, Any]:
        """Handle deleting a task."""
        # Extract task identifier from the message
        identifier = self._extract_task_identifier(message)

        if not identifier:
            return {
                "response": "I couldn't identify which task to delete. Please specify the task title.",
                "tasks_updated": [],
                "next_message_expected": True
            }

        # Find the task by identifier
        task = self._find_task_by_identifier(identifier, user_id)

        if not task:
            return {
                "response": f"I couldn't find a task matching '{identifier}'. Please check the task name and try again.",
                "tasks_updated": [],
                "next_message_expected": True
            }

        # Delete the task
        result = self.mcp_tools.delete_task(task_id=task["id"], user_id=user_id)

        if result["success"]:
            return {
                "response": f"I've deleted the task '{task['title']}'.",
                "tasks_updated": [{"id": task["id"], "title": task["title"], "operation": "deleted"}],
                "next_message_expected": False
            }
        else:
            return {
                "response": f"Sorry, I couldn't delete the task: {result['error']}",
                "tasks_updated": [],
                "next_message_expected": False
            }

    def _handle_update_task(self, message: str, user_id: str) -> Dict[str, Any]:
        """Handle updating a task."""
        # This is a simplified implementation - in reality, you'd need to identify which task to update
        # and what changes to make
        return {
            "response": "To update a task, please specify which task and what changes you want to make. For example: 'Change the meeting task title to team sync'.",
            "tasks_updated": [],
            "next_message_expected": True
        }
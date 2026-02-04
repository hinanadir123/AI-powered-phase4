from typing import Dict, Any, Optional
from sqlmodel import Session
from .task_service import TaskService
from ..models.task import Task


class MCPTaskTools:
    """Class to expose task operations as MCP tools."""
    
    def __init__(self, session: Session):
        self.task_service = TaskService(session)
    
    def add_task(self, title: str, description: Optional[str] = None, user_id: str = None) -> Dict[str, Any]:
        """Create a new task for the authenticated user."""
        try:
            task = self.task_service.add_task(title=title, description=description, user_id=user_id)
            
            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "created_at": task.created_at.isoformat(),
                    "user_id": task.user_id
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "SERVER_ERROR"
            }
    
    def list_tasks(self, user_id: str, status_filter: Optional[str] = "all") -> Dict[str, Any]:
        """Retrieve all tasks for the authenticated user, with optional filtering."""
        try:
            tasks = self.task_service.list_tasks(user_id=user_id, status_filter=status_filter)
            
            return {
                "success": True,
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "created_at": task.created_at.isoformat(),
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                        "user_id": task.user_id
                    } for task in tasks
                ],
                "total_count": len(tasks)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "SERVER_ERROR"
            }
    
    def complete_task(self, task_id: str, user_id: str) -> Dict[str, Any]:
        """Mark a specific task as completed."""
        try:
            task = self.task_service.complete_task(task_id=task_id, user_id=user_id)
            
            if task:
                return {
                    "success": True,
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "status": task.status,
                        "completed_at": task.completed_at.isoformat()
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Task not found",
                    "error_code": "RESOURCE_NOT_FOUND"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "SERVER_ERROR"
            }
    
    def delete_task(self, task_id: str, user_id: str) -> Dict[str, Any]:
        """Delete a specific task."""
        try:
            success = self.task_service.delete_task(task_id=task_id, user_id=user_id)
            
            if success:
                return {
                    "success": True,
                    "task_id": task_id,
                    "message": "Task deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Task not found",
                    "error_code": "RESOURCE_NOT_FOUND"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "SERVER_ERROR"
            }
    
    def update_task(self, task_id: str, user_id: str, title: Optional[str] = None, 
                   description: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """Update the details of a specific task."""
        try:
            task = self.task_service.update_task(
                task_id=task_id, 
                user_id=user_id, 
                title=title, 
                description=description, 
                status=status
            )
            
            if task:
                return {
                    "success": True,
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "updated_at": task.created_at.isoformat()  # Using created_at as updated_at for now
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Task not found",
                    "error_code": "RESOURCE_NOT_FOUND"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "SERVER_ERROR"
            }
from sqlmodel import Session, select
from datetime import datetime
from typing import List, Optional
from ..models.task import Task
from ..models.user import User


class TaskService:
    """Service class to handle task-related operations."""

    def __init__(self, session: Session):
        self.session = session

    def add_task(self, title: str, description: Optional[str] = None, user_id: str = None, conversation_id: Optional[str] = None) -> Task:
        """Create a new task."""
        task = Task(
            title=title,
            description=description,
            user_id=user_id,
            conversation_id=conversation_id
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def list_tasks(self, user_id: str, status_filter: Optional[str] = "all") -> List[Task]:
        """Retrieve all tasks for a user, with optional filtering."""
        query = select(Task).where(Task.user_id == user_id)

        if status_filter and status_filter != "all":
            if status_filter in ["pending", "completed"]:
                query = query.where(Task.status == status_filter)

        tasks = self.session.exec(query).all()
        return tasks

    def complete_task(self, task_id: str, user_id: str) -> Optional[Task]:
        """Mark a specific task as completed."""
        task = self.get_task_by_id_and_user(task_id, user_id)
        if task:
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)
        return task

    def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete a specific task."""
        task = self.get_task_by_id_and_user(task_id, user_id)
        if task:
            self.session.delete(task)
            self.session.commit()
            return True
        return False

    def update_task(self, task_id: str, user_id: str, title: Optional[str] = None,
                    description: Optional[str] = None, status: Optional[str] = None) -> Optional[Task]:
        """Update the details of a specific task."""
        task = self.get_task_by_id_and_user(task_id, user_id)
        if task:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if status is not None and status in ["pending", "completed"]:
                task.status = status

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)
        return task

    def get_task_by_id_and_user(self, task_id: str, user_id: str) -> Optional[Task]:
        """Get a specific task by its ID and user ID."""
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = self.session.exec(query).first()
        return task
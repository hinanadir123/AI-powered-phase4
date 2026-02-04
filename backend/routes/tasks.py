from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, desc, asc
from typing import List
from datetime import datetime
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskRead
from db import get_session
from dependencies import get_current_user

router = APIRouter(prefix="/api/{user_id}", tags=["tasks"])


@router.get("/tasks", response_model=List[TaskRead])
def get_tasks(
    user_id: str,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
    status_param: str = Query("all", regex="^(all|pending|completed)$"),
    sort: str = Query("created", regex="^(created|title)$")
):
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    # Build query based on status filter
    query = select(Task).where(Task.user_id == user_id)

    if status_param == "pending":
        query = query.where(Task.completed == False)
    elif status_param == "completed":
        query = query.where(Task.completed == True)

    # Apply sorting
    if sort == "title":
        query = query.order_by(asc(Task.title))
    else:  # Default to created date (descending for newest first)
        query = query.order_by(desc(Task.created_at))

    tasks = session.exec(query).all()
    return tasks


@router.post("/tasks", response_model=TaskRead)
def create_task(
    user_id: str,
    task: TaskCreate,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)):
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    # Validate title length
    if len(task.title) < 1 or len(task.title) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be between 1 and 200 characters"
        )

    db_task = Task(
        title=task.title,
        description=task.description,
        user_id=user_id,
        completed=False
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.get("/tasks/{id}", response_model=TaskRead)
def get_task(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)):
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify that the task belongs to the user
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: task does not belong to user"
        )

    return task


@router.put("/tasks/{id}", response_model=TaskRead)
def update_task(
    user_id: str,
    id: int,
    task_update: TaskUpdate,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)):
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    db_task = session.get(Task, id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify that the task belongs to the user
    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: task does not belong to user"
        )

    # Update fields if provided
    if task_update.title is not None:
        if len(task_update.title) < 1 or len(task_update.title) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title must be between 1 and 200 characters"
            )
        db_task.title = task_update.title

    if task_update.description is not None:
        db_task.description = task_update.description

    if task_update.completed is not None:
        db_task.completed = task_update.completed

    db_task.updated_at = datetime.utcnow()
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@router.delete("/tasks/{id}")
def delete_task(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)):
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    db_task = session.get(Task, id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify that the task belongs to the user
    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: task does not belong to user"
        )

    session.delete(db_task)
    session.commit()
    return {"message": "Task deleted successfully"}


@router.patch("/tasks/{id}/complete", response_model=TaskRead)
def toggle_task_complete(
    user_id: str,
    id: int,
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)):
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch"
        )

    db_task = session.get(Task, id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify that the task belongs to the user
    if db_task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: task does not belong to user"
        )

    # Toggle the completed status
    db_task.completed = not db_task.completed
    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
"""
Advanced Reminder Worker - Kafka Consumer
Task: T5.3.3 - Implements reminder event processing
Spec Reference: phase5-spec.md Section 4.4 (Event Processing)
Constitution: constitution.md v5.0

This file implements the reminder worker that subscribes to Kafka events
and processes reminder notifications using Dapr Pub/Sub via HTTP API.
"""
import asyncio
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum


class EventNotification(BaseModel):
    """Model for event notification payload"""
    event_type: str
    timestamp: str
    data: Dict[str, Any]


class EventType(str, Enum):
    """Event types that the reminder worker will handle"""
    RECURRING_TASK_CREATED = "recurring_task.created"
    DUE_DATE_SET = "due_date.set"
    REMINDER_SCHEDULED = "reminder.scheduled"
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"


app = FastAPI(title="Reminder Worker", version="1.0")


class ReminderProcessor:
    """
    Reminder Processing Service
    Subscribes to Kafka events and processes reminder notifications
    """
    def __init__(self):
        self.dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
        self.dapr_url = f"http://localhost:{self.dapr_port}"
        self.enabled = os.getenv("WORKER_ENABLED", "true").lower() == "true"
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

    def create_reminder_payload(self, task_data: Dict[str, Any], minutes_before: int = 60):
        """Create payload for reminder event"""
        due_date = datetime.fromisoformat(task_data["due_date"].replace('Z', '+00:00'))
        reminder_time = due_date - timedelta(minutes=minutes_before)

        return {
            "task_id": task_data["task_id"],
            "user_id": task_data["user_id"],
            "reminder_time": reminder_time.isoformat(),
            "due_date": due_date.isoformat(),
            "title": task_data.get("title", "Untitled Task"),
            "priority": task_data.get("priority", "medium"),
            "description": task_data.get("description", "")
        }

    def send_notification(self, reminder_payload: Dict[str, Any]):
        """Actually send a notification - this would typically go to an external service"""
        try:
            print(f"[REMINDER] Sending notification for task ID {reminder_payload['task_id']}")
            print(f"  Title: {reminder_payload['title']}")
            print(f"  Due: {reminder_payload['due_date']}")
            print(f"  Priority: {reminder_payload['priority']}")

            # In a real implementation, you could call:
            # - Email service
            # - Push notification service
            # - SMS service
            # - WebSocket broadcast to UI

            # For simulation purposes:
            return True
        except Exception as e:
            print(f"[REMINDER ERROR] Failed to send notification: {e}")
            return False

    def process_recurring_task_created(self, event_data: Dict[str, Any]):
        """Process a recurring task created event"""
        print(f"[RECURRING] Processing recurring task event: {event_data['task_id']}")
        # This could schedule the next occurrence

    def process_due_date_set(self, event_data: Dict[str, Any]):
        """Process a due date set event"""
        print(f"[DUE DATE] Processing due date event: {event_data['task_id']}")

    def process_task_completed(self, event_data: Dict[str, Any]):
        """Process a task completed event"""
        task_id = event_data['task_id'] if 'task_id' in event_data else event_data.get('data', {}).get('task_id')
        print(f"[COMPLETED] Processing completion event: {task_id}")

    def process_reminder_scheduled(self, event_data: Dict[str, Any]):
        """Process and send reminder for scheduled event"""
        print(f"[SCHEDULED] Processing reminder scheduled event: {event_data.get('task_id')}")
        reminder_payload = {
            'task_id': event_data.get('task_id'),
            'user_id': event_data.get('user_id'),
            'reminder_time': event_data.get('reminder_time'),
            'due_date': event_data.get('data', {}).get('due_date') or event_data.get('due_date'),
            'title': event_data.get('data', {}).get('title', 'Untitled Task'),
            'priority': event_data.get('data', {}).get('priority', 'medium'),
            'description': event_data.get('data', {}).get('description', '')
        }

        # Send the notification
        success = self.send_notification(reminder_payload)
        if success:
            print(f"[SUCCESS] Reminder sent for task {reminder_payload['task_id']}")
        else:
            print(f"[ERROR] Failed to send reminder for task {reminder_payload['task_id']}")

    def handle_event(self, event_notification: EventNotification):
        """Handle incoming event from Kafka"""
        try:
            event_type = event_notification.event_type
            event_data = event_notification.data

            print(f"[EVENT] Received: {event_type} at {event_notification.timestamp}")

            # Process different event types
            if event_type == "reminder.scheduled":
                self.process_reminder_scheduled(event_data)
            elif event_type == "recurring_task.created":
                self.process_recurring_task_created(event_data)
            elif event_type == "due_date.set":
                self.process_due_date_set(event_data)
            elif event_type == "task.completed":
                self.process_task_completed(event_data)
            else:
                print(f"[EVENT] Unknown event type: {event_type}")

        except Exception as e:
            print(f"[EVENT ERROR] Processing event: {e}")


# Global processor instance
processor = ReminderProcessor()


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr Subscribe endpoint - tells Dapr which topics this service will subscribe to
    """
    return [
        {
            "pubsubname": "pubsub-kafka",
            "topic": "reminders",
            "route": "/api/events/reminders"
        },
        {
            "pubsubname": "pubsub-kafka",
            "topic": "task-events",
            "route": "/api/events/task-events"
        }
    ]


@app.post("/api/events/reminders")
async def handle_reminder_event(notification: EventNotification):
    """
    Handle reminder events from Kafka
    """
    processor.handle_event(notification)
    return {"status": "processed"}


@app.post("/api/events/task-events")
async def handle_task_event(notification: EventNotification):
    """
    Handle task events from Kafka that might trigger reminders
    """
    processor.handle_event(notification)
    return {"status": "processed"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "processor": "running"}


@app.get("/api/process-pending-reminders")
async def process_pending_reminders():
    """
    Manual endpoint to process pending reminders
    Simulates what would be done periodically via scheduled job
    """
    print("[MANUAL] Processing pending reminders")
    # In a real implementation, this would query the database for pending reminders
    # For now, this just serves as documentation of the intent
    return {"message": "Pending reminders processing initiated"}


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "service": "Reminder Worker",
        "status": "running",
        "dapr_integration": True,
        "topics": ["reminders", "task-events"]
    }


# This would normally run as a separate service, but can also run for testing
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))  # Use different port from main app
    print(f"Launching Reminder Worker on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
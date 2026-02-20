"""
Dapr Event-Driven Reminder Worker
Task: T5.3.3 - Implements phase5-spec.md Section 3.2.2 (Event Subscribers)
Constitution: constitution.md v5.0 Section 2.3 (No Direct Kafka SDK imports)
"""

import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
import uvicorn


class DaprReminderWorker:
    """Reminder worker that processes events from Kafka via Dapr Pub/Sub"""

    def __init__(self, dapr_endpoint: str = "http://localhost:3500"):
        self.dapr_endpoint = dapr_endpoint
        self.pubsub_name = "kafka-pubsub"
        self.reminders_topic = "reminders"
        self.task_events_topic = "task-events"
        self.jobs_component = "dapr-jobs"

    def handle_task_events(self, cloudevent: Dict[str, Any]) -> None:
        """
        Handle task-related events that may trigger reminder scheduling
        """
        event_type = cloudevent.get('type', '')
        data = cloudevent.get('data', {})

        print(f"Processing task event: {event_type} for task {cloudevent.get('subject', 'unknown')}")

        if event_type == 'task.created':
            self._process_task_created(data)

        elif event_type == 'task.updated':
            # Check if due date or reminder settings changed and reschedule
            self._process_task_updated(data)

        elif event_type == 'task.status.changed':
            # Handle changes in task status that might affect reminders
            self._process_task_status_changed(data)

    def _process_task_created(self, task_data: Dict[str, Any]) -> None:
        """Process a task created event and schedule reminder if needed"""
        print(f"Processing task created event for task: {task_data.get('id')}")

        # Check if task has due date and reminder enabled
        due_date = task_data.get('due_date')
        reminder_config = task_data.get('reminder', {})

        if due_date and reminder_config.get('enabled', False):
            # Calculate reminder time
            reminder_time = self._calculate_reminder_time(due_date, reminder_config.get('time_before', '1h'))

            # Schedule reminder via Dapr Jobs API
            job_name = f"reminder-{task_data['id']}"
            self.schedule_reminder_job(job_name, task_data['id'], reminder_time, task_data.get('title', ''))
            print(f"Scheduled reminder job for task {task_data['id']} at {reminder_time}")

    def _process_task_updated(self, task_data: Dict[str, Any]) -> None:
        """Process a task updated event and reschedule if needed"""
        print(f"Processing task updated event for task: {task_data.get('id')}")

        # For simplicity, reschedule if due date has changed
        if 'due_date' in task_data or 'reminder' in task_data:
            # Cancel existing job and reschedule
            job_name = f"reminder-{task_data['id']}"
            self._cancel_existing_job(job_name)

            due_date = task_data.get('due_date')
            reminder_config = task_data.get('reminder', {})

            if due_date and reminder_config.get('enabled', True):
                reminder_time = self._calculate_reminder_time(due_date, reminder_config.get('time_before', '1h'))
                self.schedule_reminder_job(job_name, task_data['id'], reminder_time, task_data.get('title', ''))
                print(f"Rescheduled reminder job for task {task_data['id']} at {reminder_time}")

    def _process_task_status_changed(self, task_data: Dict[str, Any]) -> None:
        """Process a task status change event"""
        print(f"Processing task status changed for task: {task_data.get('id')}")

        # If task is completed, cancel the reminder
        if task_data.get('status') == 'completed':
            job_name = f"reminder-{task_data['id']}"
            self._cancel_existing_job(job_name)
            print(f"Cancelled reminder job for completed task {task_data['id']}")

    def _calculate_reminder_time(self, due_date: str, time_before: str) -> str:
        """Calculate the reminder time based on due date and time before reminder"""
        due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00')).replace(tzinfo=None)

        # Parse time_before (like '1h', '2d', '30m')
        if time_before.endswith('h'):
            delta = timedelta(hours=int(time_before[:-1]))
        elif time_before.endswith('d'):
            delta = timedelta(days=int(time_before[:-1]))
        elif time_before.endswith('m'):
            delta = timedelta(minutes=int(time_before[:-1]))
        elif time_before.endswith('s'):
            delta = timedelta(seconds=int(time_before[:-1]))
        else:
            # Default to 1 hour before
            delta = timedelta(hours=1)

        reminder_time = due_datetime - delta

        # Don't schedule in the past
        if reminder_time <= datetime.utcnow():
            reminder_time = datetime.utcnow() + timedelta(minutes=1)  # Schedule in 1 minute if already passed

        return reminder_time.isoformat() + 'Z'

    def schedule_reminder_job(self, job_name: str, task_id: str, reminder_time: str, task_title: str) -> bool:
        """Schedule a reminder job using Dapr Jobs API"""
        job_data = {
            "name": job_name,
            "schedule": reminder_time,
            "data": {
                "task_id": task_id,
                "task_title": task_title,
                "execution_time": reminder_time,
                "type": "reminder"
            },
            "metadata": {
                "category": "reminder",
                "priority": "medium"
            },
            "repeats": 1  # One-time execution
        }

        url = f"{self.dapr_endpoint}/v1.0-alpha1/workflows/{self.jobs_component}"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=job_data, headers=headers, timeout=30)

            if response.status_code == 200:
                print(f"Reminder job scheduled successfully: {job_name}")
                return True
            else:
                print(f"Failed to schedule reminder job: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error scheduling reminder job: {e}")
            return False

    def _cancel_existing_job(self, job_name: str) -> bool:
        """Cancel an existing job by name"""
        url = f"{self.dapr_endpoint}/v1.0-alpha1/workflows/{self.jobs_component}/{job_name}"

        try:
            response = requests.delete(url, timeout=30)
            if response.status_code in [200, 204]:
                print(f"Job {job_name} cancelled successfully")
                return True
            else:
                print(f"Failed to cancel job {job_name}: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error cancelling job {job_name}: {e}")
            return False

    def execute_reminder_job(self, task_id: str, task_title: str) -> None:
        """Execute the reminder notification when a reminder job runs"""
        print(f"Executing reminder for task {task_id}: {task_title}")

        # This could send notifications to multiple channels (email, push, etc.)
        # For now, just publish a reminder event back to Kafka
        publisher = ReminderEventPublisher(self.dapr_endpoint)
        publisher.publish_reminder_triggered(
            task_id=task_id,
            message=f"Reminder: Task '{task_title}' is due soon!",
            channels=["push", "email"],
            user_id="system"
        )


# Create the FastAPI app to handle Dapr Pub/Sub subscriptions
app = FastAPI(title="Dapr Reminder Worker", version="1.0.0")

# Initialize the worker
worker = DaprReminderWorker()
from backend.events.reminder_publisher import ReminderEventPublisher


@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr subscription endpoint - tells Dapr which topics to subscribe to"""
    subscriptions = [
        {
            "pubsubname": worker.pubsub_name,
            "topic": "task-events",
            "route": "/task-events",
            "metadata": {
                "consumerGroup": "reminder-worker-task-events"
            },
            "deadLetterTopic": "task-events-dlq"
        },
        {
            "pubsubname": worker.pubsub_name,
            "topic": "reminders",
            "route": "/reminders",
            "metadata": {
                "consumerGroup": "reminder-worker-reminders"
            },
            "deadLetterTopic": "reminders-dlq"
        }
    ]
    return subscriptions


@app.post("/task-events")
async def handle_task_events(cloudevent: Dict[str, Any]):
    """Handle incoming task events from Kafka"""
    print(f"Received task event: {cloudevent.get('type', 'unknown')}")
    try:
        worker.handle_task_events(cloudevent)
        return {"status": "success"}
    except Exception as e:
        print(f"Error processing task event: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/reminders")
async def handle_reminders(cloudevent: Dict[str, Any]):
    """Handle incoming reminder events"""
    print(f"Received reminder event: {cloudevent.get('type', 'unknown')}")
    try:
        # Process reminder-specific events like failed reminders, manual triggers, etc.
        event_type = cloudevent.get('type', '')

        if event_type == 'reminder.failed':
            # Handle failed reminder - maybe retry or send alert
            data = cloudevent.get('data', {})
            print(f"Reminder failed for task {data.get('task_id')}: {data.get('error_message')}")

        elif event_type == 'reminder.cancelled':
            # Handle reminder cancellation
            data = cloudevent.get('data', {})
            print(f"Reminder cancelled for task {data.get('task_id')}: {data.get('reason')}")

        return {"status": "success"}
    except Exception as e:
        print(f"Error processing reminder event: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/workflow/reminder/{workflow_id}")
async def execute_reminder_workflow(workflow_id: str):
    """Execute the actual reminder workflow when scheduled"""
    # This is triggered by Dapr when a scheduled job runs
    try:
        # In real implementation, this would retrieve task details from database
        # For demo, we'll just log that the workflow executed
        print(f"Reminder workflow executed: {workflow_id}")

        return {"status": "reminder_executed", "workflow_id": workflow_id}
    except Exception as e:
        print(f"Error in reminder workflow: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "component": "reminder-worker"}


# For testing the worker independently
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
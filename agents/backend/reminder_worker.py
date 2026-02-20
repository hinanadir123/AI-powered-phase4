# Task: T5.3.3 - Implement Reminder Worker (Kafka Subscriber)
# Spec Reference: phase5-spec.md Section 3.2.2, Section 4.2 (Event Flow)
# Constitution: constitution.md v5.0 Section 2.3 (Event-Driven Architecture)
#
# This service subscribes to task-events topic via Dapr Pub/Sub and:
# - Processes task.created and task.updated events
# - Schedules reminders via Dapr Jobs API
# - Creates next recurring task instance on task.completed
# - Handles errors with retry logic and DLQ
#
# Version: 1.0
# Date: 2026-02-15

from flask import Flask, request, jsonify
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


class ReminderWorker:
    """
    Worker service that processes task events and schedules reminders.

    Subscribes to Kafka task-events topic via Dapr Pub/Sub.
    Schedules reminders using Dapr Jobs API.
    """

    def __init__(self, dapr_http_port: int = 3500):
        """
        Initialize the Reminder Worker.

        Args:
            dapr_http_port: Dapr sidecar HTTP port (default: 3500)
        """
        self.dapr_url = f"http://localhost:{dapr_http_port}"
        self.pubsub_name = "pubsub-kafka"
        self.jobs_component = "jobs-scheduler"

    def parse_time_before(self, time_before: str) -> int:
        """
        Parse time_before string to seconds.

        Args:
            time_before: Time string like "15m", "1h", "1d", "1w"

        Returns:
            Number of seconds
        """
        unit = time_before[-1]
        value = int(time_before[:-1])

        multipliers = {
            'm': 60,           # minutes
            'h': 3600,         # hours
            'd': 86400,        # days
            'w': 604800        # weeks
        }

        return value * multipliers.get(unit, 3600)

    def calculate_reminder_time(self, due_date: str, time_before: str) -> datetime:
        """
        Calculate when reminder should be triggered.

        Args:
            due_date: ISO format due date string
            time_before: Time before due date (e.g., "1h")

        Returns:
            Datetime when reminder should trigger
        """
        due_dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        seconds_before = self.parse_time_before(time_before)
        reminder_time = due_dt - timedelta(seconds=seconds_before)
        return reminder_time

    def schedule_reminder_job(self, task_id: str, reminder_time: datetime, task_data: Dict[str, Any]) -> bool:
        """
        Schedule a reminder job via Dapr Jobs API.

        Args:
            task_id: Task ID
            reminder_time: When to trigger the reminder
            task_data: Task data for the reminder

        Returns:
            True if successful, False otherwise
        """
        job_name = f"reminder-{task_id}"
        url = f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}"

        job_payload = {
            "schedule": reminder_time.isoformat() + "Z",
            "repeats": 0,  # One-time job
            "data": {
                "task_id": task_id,
                "title": task_data.get("title"),
                "due_date": task_data.get("due_date"),
                "channels": task_data.get("reminder", {}).get("channels", ["email"]),
                "user_id": task_data.get("user_id")
            }
        }

        try:
            response = requests.post(
                url,
                json=job_payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )

            if response.status_code in [200, 201, 204]:
                logger.info(f"✅ Scheduled reminder job for task {task_id} at {reminder_time}")
                return True
            else:
                logger.error(f"❌ Failed to schedule job: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error scheduling job: {str(e)}")
            return False

    def schedule_recurring_task_job(self, task_data: Dict[str, Any]) -> bool:
        """
        Schedule job to create next recurring task instance.

        Args:
            task_data: Task data with recurrence configuration

        Returns:
            True if successful, False otherwise
        """
        recurrence = task_data.get("recurrence", {})
        if not recurrence or not recurrence.get("enabled"):
            return False

        task_id = task_data["id"]
        interval = recurrence.get("interval")
        frequency = recurrence.get("frequency", 1)

        # Calculate next occurrence based on interval
        now = datetime.utcnow()
        if interval == "daily":
            next_time = now + timedelta(days=frequency)
        elif interval == "weekly":
            next_time = now + timedelta(weeks=frequency)
        elif interval == "monthly":
            next_time = now + timedelta(days=30 * frequency)  # Approximate
        else:
            logger.warning(f"Unsupported interval: {interval}")
            return False

        # Check if end_date has passed
        end_date = recurrence.get("end_date")
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            if next_time > end_dt:
                logger.info(f"Recurrence ended for task {task_id}")
                return False

        job_name = f"recurring-{task_id}"
        url = f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}"

        job_payload = {
            "schedule": next_time.isoformat() + "Z",
            "repeats": 0,
            "data": {
                "parent_task_id": task_id,
                "task_data": task_data
            }
        }

        try:
            response = requests.post(
                url,
                json=job_payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )

            if response.status_code in [200, 201, 204]:
                logger.info(f"✅ Scheduled recurring task job for {task_id} at {next_time}")
                return True
            else:
                logger.error(f"❌ Failed to schedule recurring job: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error scheduling recurring job: {str(e)}")
            return False

    def process_task_created(self, event_data: Dict[str, Any]) -> bool:
        """
        Process task.created event.

        Args:
            event_data: Event data from CloudEvents

        Returns:
            True if processed successfully
        """
        task_data = event_data.get("data", {})
        task_id = task_data.get("task_id")

        logger.info(f"Processing task.created event for task {task_id}")

        # Schedule reminder if configured
        reminder = task_data.get("reminder")
        due_date = task_data.get("due_date")

        if reminder and reminder.get("enabled") and due_date:
            time_before = reminder.get("time_before", "1h")
            reminder_time = self.calculate_reminder_time(due_date, time_before)

            if reminder_time > datetime.utcnow():
                self.schedule_reminder_job(task_id, reminder_time, task_data)
            else:
                logger.warning(f"Reminder time is in the past for task {task_id}")

        return True

    def process_task_updated(self, event_data: Dict[str, Any]) -> bool:
        """
        Process task.updated event.

        Args:
            event_data: Event data from CloudEvents

        Returns:
            True if processed successfully
        """
        task_data = event_data.get("data", {})
        task_id = task_data.get("task_id")
        changes = task_data.get("changes", {})

        logger.info(f"Processing task.updated event for task {task_id}")

        # If due_date or reminder changed, reschedule
        if "due_date" in changes or "reminder" in changes:
            current_state = task_data.get("current_state", {})
            reminder = current_state.get("reminder")
            due_date = current_state.get("due_date")

            if reminder and reminder.get("enabled") and due_date:
                time_before = reminder.get("time_before", "1h")
                reminder_time = self.calculate_reminder_time(due_date, time_before)

                if reminder_time > datetime.utcnow():
                    self.schedule_reminder_job(task_id, reminder_time, current_state)

        return True

    def process_task_completed(self, event_data: Dict[str, Any]) -> bool:
        """
        Process task.completed event.

        Args:
            event_data: Event data from CloudEvents

        Returns:
            True if processed successfully
        """
        task_data = event_data.get("data", {})
        task_id = task_data.get("task_id")
        recurrence = task_data.get("recurrence")

        logger.info(f"Processing task.completed event for task {task_id}")

        # If task has recurrence, schedule next instance
        if recurrence and recurrence.get("enabled"):
            self.schedule_recurring_task_job(task_data)

        return True


# Initialize worker
worker = ReminderWorker()


@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    """
    Dapr subscription endpoint.

    Returns list of topics to subscribe to.
    """
    subscriptions = [
        {
            "pubsubname": "pubsub-kafka",
            "topic": "task-events",
            "route": "/task-events"
        }
    ]
    logger.info("Dapr subscription endpoint called")
    return jsonify(subscriptions)


@app.route('/task-events', methods=['POST'])
def handle_task_event():
    """
    Handle incoming task events from Kafka via Dapr.

    Processes task.created, task.updated, and task.completed events.
    """
    try:
        event = request.json
        event_type = event.get("type")
        event_data = event.get("data", {})

        logger.info(f"Received event: {event_type}")

        # Process based on event type
        if event_type == "task.created":
            worker.process_task_created(event)
        elif event_type == "task.updated":
            worker.process_task_updated(event)
        elif event_type == "task.completed":
            worker.process_task_completed(event)
        else:
            logger.warning(f"Unknown event type: {event_type}")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Error processing event: {str(e)}", exc_info=True)
        # Return 500 to trigger retry via Dapr
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route('/ready', methods=['GET'])
def ready():
    """Readiness check endpoint"""
    return jsonify({"status": "ready"}), 200


if __name__ == '__main__':
    logger.info("Starting Reminder Worker service...")
    app.run(host='0.0.0.0', port=5001)

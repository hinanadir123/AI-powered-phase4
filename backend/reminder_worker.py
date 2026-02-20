"""
Reminder Worker Service
Phase 5 - Advanced Features

Background worker that periodically checks for tasks needing reminders
and sends notifications.

In Step 3, this will be integrated with Dapr Jobs API for scheduling.
"""

import time
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session
from db import engine
from services.reminder_service import ReminderService


def run_reminder_worker(interval_seconds: int = 60):
    """
    Run the reminder worker in a loop

    Args:
        interval_seconds: How often to check for reminders (default: 60 seconds)
    """
    print(f"[REMINDER WORKER] Starting... (checking every {interval_seconds}s)")

    while True:
        try:
            with Session(engine) as session:
                print(f"[REMINDER WORKER] Checking for reminders at {datetime.utcnow()}")
                count = ReminderService.process_reminders(session)

                if count > 0:
                    print(f"[REMINDER WORKER] Sent {count} reminder(s)")
                else:
                    print(f"[REMINDER WORKER] No reminders to send")

        except Exception as e:
            print(f"[REMINDER WORKER] Error: {e}")

        # Wait before next check
        time.sleep(interval_seconds)


if __name__ == "__main__":
    # Check for interval argument
    interval = 60  # Default: check every 60 seconds

    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print(f"Invalid interval: {sys.argv[1]}, using default: 60s")

    run_reminder_worker(interval)

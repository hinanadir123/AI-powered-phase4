# Task: T5.3.1, T5.3.5 - Database Migration for Advanced Features
# Spec Reference: phase5-spec.md Section 3.2 (Advanced Features)
# Constitution: constitution.md v5.0 Section 4.4
#
# This migration adds:
# - due_date field
# - recurrence JSON field
# - reminder JSON field
# - parent_task_id field for recurring tasks
# - updated_at field
#
# Version: 1.0
# Date: 2026-02-15

"""
Database migration script for adding advanced features to Task model.

Usage:
    python migration_advanced_features.py

This script adds the following columns to the tasks table:
- due_date: TIMESTAMP (nullable)
- recurrence: JSON (nullable)
- reminder: JSON (nullable)
- parent_task_id: VARCHAR (nullable)
- updated_at: TIMESTAMP (default: current_timestamp)
"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os
from datetime import datetime


def get_database_url():
    """Get database URL from environment or use default"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/todo_db"
    )


def run_migration():
    """Execute the migration to add advanced features to tasks table"""
    engine = create_engine(get_database_url())

    migration_sql = """
    -- Migration: Add Advanced Features to Tasks Table
    -- Date: 2026-02-15
    -- Tasks: T5.3.1, T5.3.5

    BEGIN;

    -- Add due_date column
    ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS due_date TIMESTAMP NULL;

    -- Add recurrence JSON column
    ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS recurrence JSONB NULL;

    -- Add reminder JSON column
    ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS reminder JSONB NULL;

    -- Add parent_task_id for recurring tasks
    ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS parent_task_id VARCHAR NULL;

    -- Add updated_at timestamp
    ALTER TABLE tasks
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

    -- Update existing rows to have updated_at = created_at
    UPDATE tasks
    SET updated_at = created_at
    WHERE updated_at IS NULL;

    -- Create index on due_date for faster queries
    CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);

    -- Create index on parent_task_id for recurring tasks
    CREATE INDEX IF NOT EXISTS idx_tasks_parent_task_id ON tasks(parent_task_id);

    -- Create index on priority for filtering
    CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);

    -- Create GIN index on tags for array searches
    CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks USING GIN(tags);

    -- Update status check constraint to include 'in-progress'
    ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_status_check;
    ALTER TABLE tasks ADD CONSTRAINT tasks_status_check
        CHECK (status IN ('pending', 'in-progress', 'completed'));

    COMMIT;
    """

    try:
        with engine.connect() as conn:
            print("Starting migration...")
            conn.execute(text(migration_sql))
            conn.commit()
            print("✅ Migration completed successfully!")
            print("Added columns: due_date, recurrence, reminder, parent_task_id, updated_at")
            print("Created indexes: idx_tasks_due_date, idx_tasks_parent_task_id, idx_tasks_priority, idx_tasks_tags")
    except SQLAlchemyError as e:
        print(f"❌ Migration failed: {str(e)}")
        raise


def rollback_migration():
    """Rollback the migration (remove added columns)"""
    engine = create_engine(get_database_url())

    rollback_sql = """
    -- Rollback: Remove Advanced Features from Tasks Table

    BEGIN;

    -- Drop indexes
    DROP INDEX IF EXISTS idx_tasks_due_date;
    DROP INDEX IF EXISTS idx_tasks_parent_task_id;
    DROP INDEX IF EXISTS idx_tasks_priority;
    DROP INDEX IF EXISTS idx_tasks_tags;

    -- Drop columns
    ALTER TABLE tasks DROP COLUMN IF EXISTS due_date;
    ALTER TABLE tasks DROP COLUMN IF EXISTS recurrence;
    ALTER TABLE tasks DROP COLUMN IF EXISTS reminder;
    ALTER TABLE tasks DROP COLUMN IF EXISTS parent_task_id;
    ALTER TABLE tasks DROP COLUMN IF EXISTS updated_at;

    -- Restore original status constraint
    ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_status_check;
    ALTER TABLE tasks ADD CONSTRAINT tasks_status_check
        CHECK (status IN ('pending', 'completed'));

    COMMIT;
    """

    try:
        with engine.connect() as conn:
            print("Starting rollback...")
            conn.execute(text(rollback_sql))
            conn.commit()
            print("✅ Rollback completed successfully!")
    except SQLAlchemyError as e:
        print(f"❌ Rollback failed: {str(e)}")
        raise


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        run_migration()

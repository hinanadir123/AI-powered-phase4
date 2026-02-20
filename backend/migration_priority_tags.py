"""
Task: T5.2.1, T5.2.2 - Database Migration for Priorities and Tags
Spec Reference: phase5-spec.md Section 3.1.1, 3.1.2
Constitution: constitution.md v5.0

This migration script adds priority field and tags tables to the database.
"""

from sqlalchemy import text
from sqlmodel import Session, create_engine


def upgrade_priority_and_tags(session: Session):
    """
    Add priority field to tasks table and create tags tables.
    Tasks: T5.2.1, T5.2.2
    """

    # T5.2.1: Add priority column to task table
    print("Adding priority column to task table...")
    session.exec(text("""
        ALTER TABLE task
        ADD COLUMN priority VARCHAR(10) DEFAULT 'medium' NOT NULL
    """))

    # Create index on priority for efficient filtering
    session.exec(text("""
        CREATE INDEX idx_task_priority ON task(priority)
    """))

    # T5.2.2: Create tags table
    print("Creating tags table...")
    session.exec(text("""
        CREATE TABLE IF NOT EXISTS tags (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))

    # Create index on tag name for efficient lookups
    session.exec(text("""
        CREATE INDEX idx_tags_name ON tags(name)
    """))

    # T5.2.2: Create task_tags association table
    print("Creating task_tags association table...")
    session.exec(text("""
        CREATE TABLE IF NOT EXISTS task_tags (
            task_id VARCHAR(36) NOT NULL,
            tag_id VARCHAR(36) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (task_id, tag_id),
            FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
    """))

    # Create indexes for efficient queries
    session.exec(text("""
        CREATE INDEX idx_task_tags_task_id ON task_tags(task_id)
    """))

    session.exec(text("""
        CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id)
    """))

    session.commit()
    print("Migration completed successfully!")


def downgrade_priority_and_tags(session: Session):
    """
    Rollback priority and tags migration.
    """
    print("Rolling back priority and tags migration...")

    # Drop task_tags table
    session.exec(text("DROP TABLE IF EXISTS task_tags"))

    # Drop tags table
    session.exec(text("DROP TABLE IF EXISTS tags"))

    # Drop priority column and index
    session.exec(text("DROP INDEX IF EXISTS idx_task_priority"))
    session.exec(text("ALTER TABLE task DROP COLUMN IF EXISTS priority"))

    session.commit()
    print("Rollback completed successfully!")


if __name__ == "__main__":
    """
    Run migration script directly.
    Usage: python migration_priority_tags.py
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/todo_db")
    engine = create_engine(database_url)

    with Session(engine) as session:
        try:
            upgrade_priority_and_tags(session)
        except Exception as e:
            print(f"Migration failed: {e}")
            session.rollback()
            raise

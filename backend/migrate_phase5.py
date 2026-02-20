"""
Phase 5 Database Migration Script
Adds Phase 5 fields to existing tasks table and creates tags/task_tags tables
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_dev.db")

def run_migration():
    """Run Phase 5 database migration"""
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("Starting Phase 5 migration...")

        try:
            # Add Phase 5 columns to tasks table
            print("Adding Phase 5 columns to tasks table...")

            # Check if columns already exist before adding
            migrations = [
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium' NOT NULL",
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP",
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_time TIMESTAMP",
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(20)",
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_end_date TIMESTAMP",
                "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS parent_task_id INTEGER",
                "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)",
                "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)",
            ]

            for migration in migrations:
                try:
                    conn.execute(text(migration))
                    conn.commit()
                    print(f"[OK] Executed: {migration[:60]}...")
                except Exception as e:
                    print(f"[SKIP] Already exists: {migration[:60]}...")

            # Create tags table
            print("\nCreating tags table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS tags (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            print("[OK] Tags table created")

            # Create task_tags junction table
            print("Creating task_tags table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS task_tags (
                    task_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (task_id, tag_id),
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """))
            conn.commit()
            print("[OK] Task_tags table created")

            # Create indexes
            print("\nCreating indexes...")
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)"))
            conn.commit()
            print("[OK] Indexes created")

            print("\n[SUCCESS] Phase 5 migration completed successfully!")

        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    run_migration()

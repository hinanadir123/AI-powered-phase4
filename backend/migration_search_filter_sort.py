"""
Task: T5.2.3, T5.2.4, T5.2.5 - Database Migration for Search, Filter, Sort
Spec Reference: phase5-spec.md Sections 3.1.3, 3.1.4, 3.1.5
Constitution: constitution.md v5.0

This migration adds:
- T5.2.4: due_date field to Task table for filtering and sorting
- T5.2.3: Indexes on title for search performance
- T5.2.4, T5.2.5: Composite indexes for common query patterns

Performance requirement: < 500ms for all operations (phase5-spec.md Section 5.6)
"""

from alembic import op
import sqlalchemy as sa
from datetime import date


# Revision identifiers
revision = 'add_search_filter_sort'
down_revision = 'add_priority_tags'  # Previous migration
branch_labels = None
depends_on = None


def upgrade():
    """
    Add search, filter, and sort support to Task table.
    """
    # T5.2.4: Add due_date field for filtering and sorting
    op.add_column('task', sa.Column('due_date', sa.Date(), nullable=True))

    # T5.2.3: Create index on title for search performance
    op.create_index('idx_task_title', 'task', ['title'])

    # T5.2.4: Create index on due_date for filtering and sorting
    op.create_index('idx_task_due_date', 'task', ['due_date'])

    # T5.2.4, T5.2.5: Create composite indexes for common query patterns
    # These improve performance for multi-criteria filtering

    # Index for user + status filtering
    op.create_index('idx_task_user_status', 'task', ['user_id', 'status'])

    # Index for user + priority filtering
    op.create_index('idx_task_user_priority', 'task', ['user_id', 'priority'])

    # Index for user + due_date filtering and sorting
    op.create_index('idx_task_user_due_date', 'task', ['user_id', 'due_date'])

    # Index for user + created_at sorting
    op.create_index('idx_task_user_created', 'task', ['user_id', 'created_at'])

    # T5.2.3: Create GIN index for full-text search on PostgreSQL
    # Note: This is PostgreSQL-specific. For other databases, use standard indexes.
    try:
        # Create tsvector column for full-text search
        op.execute("""
            ALTER TABLE task
            ADD COLUMN search_vector tsvector
            GENERATED ALWAYS AS (
                to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
            ) STORED;
        """)

        # Create GIN index on search_vector for fast full-text search
        op.create_index(
            'idx_task_search_vector',
            'task',
            ['search_vector'],
            postgresql_using='gin'
        )
    except Exception as e:
        # If PostgreSQL-specific features fail, fall back to standard indexes
        print(f"Warning: Could not create full-text search index: {e}")
        print("Falling back to standard LIKE-based search")


def downgrade():
    """
    Remove search, filter, and sort support from Task table.
    """
    # Drop indexes
    try:
        op.drop_index('idx_task_search_vector', table_name='task')
        op.execute("ALTER TABLE task DROP COLUMN IF EXISTS search_vector;")
    except Exception:
        pass

    op.drop_index('idx_task_user_created', table_name='task')
    op.drop_index('idx_task_user_due_date', table_name='task')
    op.drop_index('idx_task_user_priority', table_name='task')
    op.drop_index('idx_task_user_status', table_name='task')
    op.drop_index('idx_task_due_date', table_name='task')
    op.drop_index('idx_task_title', table_name='task')

    # Drop due_date column
    op.drop_column('task', 'due_date')

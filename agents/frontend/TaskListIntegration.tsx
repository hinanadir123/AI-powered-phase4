/**
 * Task: T5.2.3, T5.2.4, T5.2.5 - TaskList Integration Example
 * Spec Reference: phase5-spec.md Sections 3.1.3, 3.1.4, 3.1.5
 * Constitution: constitution.md v5.0
 *
 * Complete integration example showing how to use all search, filter, and sort components together.
 * This demonstrates the full implementation of Tasks T5.2.3, T5.2.4, T5.2.5.
 */

import React, { useState, useEffect, useCallback } from 'react';
import SearchBar from './SearchBar';
import FilterPanel, { FilterOptions } from './FilterPanel';
import SortSelect, { SortOption } from './SortSelect';
import TagChips from './TagChips';
import PriorityDropdown, { PriorityLevel } from './PriorityDropdown';

interface Task {
  id: string;
  title: string;
  description?: string;
  status: string;
  priority: PriorityLevel;
  tags: string[];
  due_date?: string;
  created_at: string;
  completed_at?: string;
}

interface TaskListResponse {
  tasks: Task[];
  total: number;
  filters_applied: Record<string, any>;
}

export const TaskListIntegration: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableTags, setAvailableTags] = useState<string[]>([]);

  // Search, filter, and sort state
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({});
  const [sort, setSort] = useState<SortOption>({ field: 'created_at', direction: 'desc' });

  // Fetch tasks from API
  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Build query parameters
      const params = new URLSearchParams();

      // T5.2.3: Add search parameter
      if (searchQuery) {
        params.append('search', searchQuery);
      }

      // T5.2.4: Add filter parameters
      if (filters.status) {
        params.append('status', filters.status);
      }
      if (filters.priority) {
        params.append('priority', filters.priority);
      }
      if (filters.tags && filters.tags.length > 0) {
        params.append('tags', filters.tags.join(','));
      }
      if (filters.due_from) {
        params.append('due_from', filters.due_from);
      }
      if (filters.due_to) {
        params.append('due_to', filters.due_to);
      }

      // T5.2.5: Add sort parameter
      params.append('sort', `${sort.field}:${sort.direction}`);

      // Make API request
      const response = await fetch(`/api/tasks?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch tasks');
      }

      const data: TaskListResponse = await response.json();
      setTasks(data.tasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [searchQuery, filters, sort]);

  // Fetch available tags
  const fetchTags = useCallback(async () => {
    try {
      const response = await fetch('/api/tasks/tags', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const tags = await response.json();
        setAvailableTags(tags.map((t: any) => t.name));
      }
    } catch (err) {
      console.error('Failed to fetch tags:', err);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchTasks();
    fetchTags();
  }, [fetchTasks, fetchTags]);

  // Update task priority
  const handlePriorityChange = async (taskId: string, priority: PriorityLevel) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ priority })
      });

      if (response.ok) {
        fetchTasks();
      }
    } catch (err) {
      console.error('Failed to update priority:', err);
    }
  };

  // Update task tags
  const handleTagsChange = async (taskId: string, tags: string[]) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ tags })
      });

      if (response.ok) {
        fetchTasks();
      }
    } catch (err) {
      console.error('Failed to update tags:', err);
    }
  };

  return (
    <div className="task-list-container">
      {/* Header with Search, Filter, and Sort */}
      <div className="task-list-header">
        <h1>My Tasks</h1>

        <div className="controls-row">
          {/* T5.2.3: Search Bar */}
          <SearchBar
            onSearch={setSearchQuery}
            placeholder="Search tasks..."
            initialValue={searchQuery}
          />

          <div className="controls-right">
            {/* T5.2.4: Filter Panel */}
            <FilterPanel
              onFilterChange={setFilters}
              availableTags={availableTags}
              initialFilters={filters}
            />

            {/* T5.2.5: Sort Select */}
            <SortSelect
              onSortChange={setSort}
              initialSort={sort}
            />
          </div>
        </div>
      </div>

      {/* Task List */}
      <div className="task-list-content">
        {loading && <div className="loading">Loading tasks...</div>}

        {error && <div className="error">{error}</div>}

        {!loading && !error && tasks.length === 0 && (
          <div className="empty-state">
            <p>No tasks found</p>
            {(searchQuery || Object.keys(filters).length > 0) && (
              <p className="empty-hint">Try adjusting your search or filters</p>
            )}
          </div>
        )}

        {!loading && !error && tasks.length > 0 && (
          <div className="tasks-grid">
            {tasks.map(task => (
              <div key={task.id} className="task-card">
                <div className="task-header">
                  <h3>{task.title}</h3>
                  {/* T5.2.1: Priority Dropdown */}
                  <PriorityDropdown
                    value={task.priority}
                    onChange={(priority) => handlePriorityChange(task.id, priority)}
                    size="small"
                  />
                </div>

                {task.description && (
                  <p className="task-description">{task.description}</p>
                )}

                {/* T5.2.2: Tag Chips */}
                <TagChips
                  tags={task.tags}
                  onTagsChange={(tags) => handleTagsChange(task.id, tags)}
                  availableTags={availableTags}
                  editable={true}
                />

                <div className="task-footer">
                  <span className="task-status">{task.status}</span>
                  {task.due_date && (
                    <span className="task-due-date">
                      Due: {new Date(task.due_date).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Results Summary */}
        {!loading && !error && (
          <div className="results-summary">
            Showing {tasks.length} task{tasks.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      <style jsx>{`
        .task-list-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 24px;
        }

        .task-list-header {
          margin-bottom: 32px;
        }

        .task-list-header h1 {
          margin: 0 0 24px 0;
          font-size: 32px;
          font-weight: 700;
          color: #1f2937;
        }

        .controls-row {
          display: flex;
          gap: 16px;
          align-items: center;
          flex-wrap: wrap;
        }

        .controls-right {
          display: flex;
          gap: 12px;
          margin-left: auto;
        }

        .task-list-content {
          min-height: 400px;
        }

        .loading,
        .error,
        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 64px 24px;
          text-align: center;
        }

        .loading {
          color: #6b7280;
        }

        .error {
          color: #ef4444;
        }

        .empty-state p {
          margin: 8px 0;
          color: #6b7280;
        }

        .empty-hint {
          font-size: 14px;
          color: #9ca3af;
        }

        .tasks-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 20px;
          margin-bottom: 24px;
        }

        .task-card {
          padding: 20px;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
          transition: all 0.2s ease;
        }

        .task-card:hover {
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          transform: translateY(-2px);
        }

        .task-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 12px;
          margin-bottom: 12px;
        }

        .task-header h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: #1f2937;
          flex: 1;
        }

        .task-description {
          margin: 0 0 16px 0;
          font-size: 14px;
          color: #6b7280;
          line-height: 1.5;
        }

        .task-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 16px;
          padding-top: 16px;
          border-top: 1px solid #e5e7eb;
          font-size: 13px;
        }

        .task-status {
          padding: 4px 8px;
          background: #f3f4f6;
          border-radius: 4px;
          color: #6b7280;
          font-weight: 500;
        }

        .task-due-date {
          color: #6b7280;
        }

        .results-summary {
          padding: 16px;
          text-align: center;
          font-size: 14px;
          color: #6b7280;
        }

        @media (max-width: 768px) {
          .controls-row {
            flex-direction: column;
            align-items: stretch;
          }

          .controls-right {
            margin-left: 0;
            justify-content: space-between;
          }

          .tasks-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default TaskListIntegration;

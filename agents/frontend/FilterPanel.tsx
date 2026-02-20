/**
 * Task: T5.2.4 - FilterPanel Component
 * Spec Reference: phase5-spec.md Section 3.1.4
 * Constitution: constitution.md v5.0
 *
 * FilterPanel component for multi-criteria task filtering.
 * Features:
 * - Filter by status (pending, completed)
 * - Filter by priority (low, medium, high, urgent)
 * - Filter by tags (multiple selection)
 * - Filter by due date range (from/to)
 * - Clear all filters button
 * - Active filter indicators
 */

import React, { useState, useEffect } from 'react';
import { Filter, X, Calendar } from 'lucide-react';

export interface FilterOptions {
  status?: string;
  priority?: string;
  tags?: string[];
  due_from?: string;
  due_to?: string;
}

interface FilterPanelProps {
  onFilterChange: (filters: FilterOptions) => void;
  availableTags?: string[];
  initialFilters?: FilterOptions;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  onFilterChange,
  availableTags = [],
  initialFilters = {}
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [filters, setFilters] = useState<FilterOptions>(initialFilters);

  useEffect(() => {
    onFilterChange(filters);
  }, [filters, onFilterChange]);

  const updateFilter = (key: keyof FilterOptions, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const toggleTag = (tag: string) => {
    setFilters(prev => {
      const currentTags = prev.tags || [];
      const newTags = currentTags.includes(tag)
        ? currentTags.filter(t => t !== tag)
        : [...currentTags, tag];
      return { ...prev, tags: newTags.length > 0 ? newTags : undefined };
    });
  };

  const clearAllFilters = () => {
    setFilters({});
  };

  const getActiveFilterCount = () => {
    let count = 0;
    if (filters.status) count++;
    if (filters.priority) count++;
    if (filters.tags && filters.tags.length > 0) count++;
    if (filters.due_from || filters.due_to) count++;
    return count;
  };

  const activeCount = getActiveFilterCount();

  return (
    <div className="filter-panel-container">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="filter-toggle-button"
        aria-label="Toggle filters"
        aria-expanded={isOpen}
      >
        <Filter size={16} />
        <span>Filters</span>
        {activeCount > 0 && (
          <span className="filter-badge">{activeCount}</span>
        )}
      </button>

      {isOpen && (
        <>
          <div className="filter-overlay" onClick={() => setIsOpen(false)} />
          <div className="filter-panel">
            <div className="filter-header">
              <h3>Filter Tasks</h3>
              <button
                onClick={() => setIsOpen(false)}
                className="close-button"
                aria-label="Close filters"
              >
                <X size={20} />
              </button>
            </div>

            <div className="filter-content">
              {/* Status Filter */}
              <div className="filter-section">
                <label className="filter-label">Status</label>
                <div className="filter-options">
                  <button
                    onClick={() => updateFilter('status', undefined)}
                    className={`filter-chip ${!filters.status ? 'active' : ''}`}
                  >
                    All
                  </button>
                  <button
                    onClick={() => updateFilter('status', 'pending')}
                    className={`filter-chip ${filters.status === 'pending' ? 'active' : ''}`}
                  >
                    Pending
                  </button>
                  <button
                    onClick={() => updateFilter('status', 'completed')}
                    className={`filter-chip ${filters.status === 'completed' ? 'active' : ''}`}
                  >
                    Completed
                  </button>
                </div>
              </div>

              {/* Priority Filter */}
              <div className="filter-section">
                <label className="filter-label">Priority</label>
                <div className="filter-options">
                  <button
                    onClick={() => updateFilter('priority', undefined)}
                    className={`filter-chip ${!filters.priority ? 'active' : ''}`}
                  >
                    All
                  </button>
                  <button
                    onClick={() => updateFilter('priority', 'low')}
                    className={`filter-chip priority-low ${filters.priority === 'low' ? 'active' : ''}`}
                  >
                    Low
                  </button>
                  <button
                    onClick={() => updateFilter('priority', 'medium')}
                    className={`filter-chip priority-medium ${filters.priority === 'medium' ? 'active' : ''}`}
                  >
                    Medium
                  </button>
                  <button
                    onClick={() => updateFilter('priority', 'high')}
                    className={`filter-chip priority-high ${filters.priority === 'high' ? 'active' : ''}`}
                  >
                    High
                  </button>
                  <button
                    onClick={() => updateFilter('priority', 'urgent')}
                    className={`filter-chip priority-urgent ${filters.priority === 'urgent' ? 'active' : ''}`}
                  >
                    Urgent
                  </button>
                </div>
              </div>

              {/* Tags Filter */}
              {availableTags.length > 0 && (
                <div className="filter-section">
                  <label className="filter-label">Tags</label>
                  <div className="filter-options">
                    {availableTags.map(tag => (
                      <button
                        key={tag}
                        onClick={() => toggleTag(tag)}
                        className={`filter-chip ${filters.tags?.includes(tag) ? 'active' : ''}`}
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Due Date Range Filter */}
              <div className="filter-section">
                <label className="filter-label">
                  <Calendar size={16} />
                  Due Date Range
                </label>
                <div className="date-range">
                  <div className="date-input-group">
                    <label htmlFor="due-from">From</label>
                    <input
                      id="due-from"
                      type="date"
                      value={filters.due_from || ''}
                      onChange={(e) => updateFilter('due_from', e.target.value || undefined)}
                      className="date-input"
                    />
                  </div>
                  <div className="date-input-group">
                    <label htmlFor="due-to">To</label>
                    <input
                      id="due-to"
                      type="date"
                      value={filters.due_to || ''}
                      onChange={(e) => updateFilter('due_to', e.target.value || undefined)}
                      className="date-input"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="filter-footer">
              <button
                onClick={clearAllFilters}
                className="clear-button"
                disabled={activeCount === 0}
              >
                Clear All Filters
              </button>
            </div>
          </div>
        </>
      )}

      <style jsx>{`
        .filter-panel-container {
          position: relative;
        }

        .filter-toggle-button {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 12px;
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          font-size: 14px;
          color: #1f2937;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .filter-toggle-button:hover {
          border-color: #d1d5db;
          background: #f9fafb;
        }

        .filter-badge {
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 20px;
          height: 20px;
          padding: 0 6px;
          background: #3b82f6;
          color: white;
          border-radius: 10px;
          font-size: 12px;
          font-weight: 600;
        }

        .filter-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.3);
          z-index: 40;
        }

        .filter-panel {
          position: absolute;
          top: calc(100% + 8px);
          right: 0;
          width: 400px;
          max-width: 90vw;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
                      0 4px 6px -2px rgba(0, 0, 0, 0.05);
          z-index: 50;
          overflow: hidden;
        }

        .filter-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 16px;
          border-bottom: 1px solid #e5e7eb;
        }

        .filter-header h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: #1f2937;
        }

        .close-button {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 4px;
          background: transparent;
          border: none;
          border-radius: 4px;
          color: #6b7280;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .close-button:hover {
          background: #f3f4f6;
          color: #1f2937;
        }

        .filter-content {
          padding: 16px;
          max-height: 500px;
          overflow-y: auto;
        }

        .filter-section {
          margin-bottom: 20px;
        }

        .filter-section:last-child {
          margin-bottom: 0;
        }

        .filter-label {
          display: flex;
          align-items: center;
          gap: 6px;
          margin-bottom: 8px;
          font-size: 13px;
          font-weight: 600;
          color: #374151;
        }

        .filter-options {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .filter-chip {
          padding: 6px 12px;
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 6px;
          font-size: 13px;
          color: #1f2937;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .filter-chip:hover {
          border-color: #d1d5db;
          background: #f9fafb;
        }

        .filter-chip.active {
          background: #3b82f6;
          border-color: #3b82f6;
          color: white;
          font-weight: 500;
        }

        .filter-chip.priority-low.active {
          background: #10b981;
          border-color: #10b981;
        }

        .filter-chip.priority-medium.active {
          background: #f59e0b;
          border-color: #f59e0b;
        }

        .filter-chip.priority-high.active {
          background: #ef4444;
          border-color: #ef4444;
        }

        .filter-chip.priority-urgent.active {
          background: #dc2626;
          border-color: #dc2626;
        }

        .date-range {
          display: flex;
          gap: 12px;
        }

        .date-input-group {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .date-input-group label {
          font-size: 12px;
          color: #6b7280;
        }

        .date-input {
          padding: 8px;
          border: 2px solid #e5e7eb;
          border-radius: 6px;
          font-size: 13px;
          color: #1f2937;
          transition: all 0.2s ease;
        }

        .date-input:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .filter-footer {
          padding: 16px;
          border-top: 1px solid #e5e7eb;
        }

        .clear-button {
          width: 100%;
          padding: 10px;
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          color: #1f2937;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .clear-button:hover:not(:disabled) {
          background: #f3f4f6;
          border-color: #d1d5db;
        }

        .clear-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default FilterPanel;

/**
 * Task: T5.2.5 - SortSelect Component
 * Spec Reference: phase5-spec.md Section 3.1.5
 * Constitution: constitution.md v5.0
 *
 * SortSelect component for sorting tasks by various fields.
 * Features:
 * - Sort by: due_date, priority, created_at, title
 * - Direction toggle (ascending/descending)
 * - Visual indicators for current sort
 * - Accessible dropdown
 */

import React, { useState } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';

export type SortField = 'due_date' | 'priority' | 'created_at' | 'title';
export type SortDirection = 'asc' | 'desc';

export interface SortOption {
  field: SortField;
  direction: SortDirection;
}

interface SortSelectProps {
  onSortChange: (sort: SortOption) => void;
  initialSort?: SortOption;
}

const sortFieldLabels: Record<SortField, string> = {
  due_date: 'Due Date',
  priority: 'Priority',
  created_at: 'Created Date',
  title: 'Title'
};

export const SortSelect: React.FC<SortSelectProps> = ({
  onSortChange,
  initialSort = { field: 'created_at', direction: 'desc' }
}) => {
  const [currentSort, setCurrentSort] = useState<SortOption>(initialSort);
  const [isOpen, setIsOpen] = useState(false);

  const handleFieldChange = (field: SortField) => {
    const newSort = { ...currentSort, field };
    setCurrentSort(newSort);
    onSortChange(newSort);
    setIsOpen(false);
  };

  const toggleDirection = () => {
    const newDirection: SortDirection = currentSort.direction === 'asc' ? 'desc' : 'asc';
    const newSort = { ...currentSort, direction: newDirection };
    setCurrentSort(newSort);
    onSortChange(newSort);
  };

  const getSortIcon = () => {
    if (currentSort.direction === 'asc') {
      return <ArrowUp size={16} />;
    }
    return <ArrowDown size={16} />;
  };

  return (
    <div className="sort-select-container">
      <div className="sort-select">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="sort-button"
          aria-label="Select sort field"
          aria-expanded={isOpen}
        >
          <ArrowUpDown size={16} />
          <span>Sort by: {sortFieldLabels[currentSort.field]}</span>
        </button>

        <button
          onClick={toggleDirection}
          className="direction-button"
          aria-label={`Sort direction: ${currentSort.direction === 'asc' ? 'ascending' : 'descending'}`}
          title={currentSort.direction === 'asc' ? 'Ascending' : 'Descending'}
        >
          {getSortIcon()}
        </button>
      </div>

      {isOpen && (
        <>
          <div className="dropdown-overlay" onClick={() => setIsOpen(false)} />
          <div className="dropdown-menu">
            {(Object.keys(sortFieldLabels) as SortField[]).map((field) => (
              <button
                key={field}
                onClick={() => handleFieldChange(field)}
                className={`dropdown-item ${currentSort.field === field ? 'active' : ''}`}
              >
                {sortFieldLabels[field]}
                {currentSort.field === field && (
                  <span className="checkmark">✓</span>
                )}
              </button>
            ))}
          </div>
        </>
      )}

      <style jsx>{`
        .sort-select-container {
          position: relative;
        }

        .sort-select {
          display: flex;
          gap: 4px;
        }

        .sort-button {
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

        .sort-button:hover {
          border-color: #d1d5db;
          background: #f9fafb;
        }

        .direction-button {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 8px;
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          color: #1f2937;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .direction-button:hover {
          border-color: #d1d5db;
          background: #f9fafb;
        }

        .dropdown-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: 10;
        }

        .dropdown-menu {
          position: absolute;
          top: calc(100% + 4px);
          left: 0;
          min-width: 200px;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                      0 2px 4px -1px rgba(0, 0, 0, 0.06);
          z-index: 20;
          overflow: hidden;
        }

        .dropdown-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          width: 100%;
          padding: 10px 14px;
          background: white;
          border: none;
          text-align: left;
          font-size: 14px;
          color: #1f2937;
          cursor: pointer;
          transition: background 0.2s ease;
        }

        .dropdown-item:hover {
          background: #f3f4f6;
        }

        .dropdown-item.active {
          background: #eff6ff;
          color: #3b82f6;
          font-weight: 500;
        }

        .checkmark {
          color: #3b82f6;
          font-weight: bold;
        }
      `}</style>
    </div>
  );
};

export default SortSelect;

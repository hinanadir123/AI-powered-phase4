/**
 * Task: T5.2.1 - PriorityDropdown Component
 * Spec Reference: phase5-spec.md Section 3.1.1
 * Constitution: constitution.md v5.0
 *
 * PriorityDropdown component for selecting task priority.
 * Features:
 * - Four priority levels: low, medium, high, urgent
 * - Color-coded visual indicators
 * - Accessible dropdown
 * - Keyboard navigation
 */

import React, { useState } from 'react';
import { ChevronDown, Flag } from 'lucide-react';

export type PriorityLevel = 'low' | 'medium' | 'high' | 'urgent';

interface PriorityDropdownProps {
  value: PriorityLevel;
  onChange: (priority: PriorityLevel) => void;
  disabled?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const priorityConfig: Record<PriorityLevel, {
  label: string;
  color: string;
  bgColor: string;
  description: string;
}> = {
  low: {
    label: 'Low',
    color: '#10b981',
    bgColor: '#d1fae5',
    description: 'Can be done later'
  },
  medium: {
    label: 'Medium',
    color: '#f59e0b',
    bgColor: '#fef3c7',
    description: 'Normal priority'
  },
  high: {
    label: 'High',
    color: '#ef4444',
    bgColor: '#fee2e2',
    description: 'Important task'
  },
  urgent: {
    label: 'Urgent',
    color: '#dc2626',
    bgColor: '#fecaca',
    description: 'Needs immediate attention'
  }
};

export const PriorityDropdown: React.FC<PriorityDropdownProps> = ({
  value,
  onChange,
  disabled = false,
  size = 'medium'
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleSelect = (priority: PriorityLevel) => {
    onChange(priority);
    setIsOpen(false);
  };

  const currentPriority = priorityConfig[value];

  const sizeClasses = {
    small: 'text-xs py-1 px-2',
    medium: 'text-sm py-2 px-3',
    large: 'text-base py-3 px-4'
  };

  return (
    <div className="priority-dropdown-container">
      <button
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`priority-button ${sizeClasses[size]} ${disabled ? 'disabled' : ''}`}
        style={{
          borderColor: currentPriority.color,
          color: currentPriority.color
        }}
        aria-label={`Priority: ${currentPriority.label}`}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <Flag size={size === 'small' ? 14 : size === 'large' ? 20 : 16} />
        <span className="priority-label">{currentPriority.label}</span>
        <ChevronDown size={size === 'small' ? 14 : size === 'large' ? 20 : 16} />
      </button>

      {isOpen && !disabled && (
        <>
          <div className="dropdown-overlay" onClick={() => setIsOpen(false)} />
          <div className="dropdown-menu" role="listbox">
            {(Object.keys(priorityConfig) as PriorityLevel[]).map((priority) => {
              const config = priorityConfig[priority];
              const isSelected = priority === value;

              return (
                <button
                  key={priority}
                  onClick={() => handleSelect(priority)}
                  className={`dropdown-item ${isSelected ? 'selected' : ''}`}
                  style={{
                    backgroundColor: isSelected ? config.bgColor : 'white',
                    borderLeft: `4px solid ${config.color}`
                  }}
                  role="option"
                  aria-selected={isSelected}
                >
                  <div className="item-content">
                    <div className="item-header">
                      <Flag size={16} style={{ color: config.color }} />
                      <span className="item-label" style={{ color: config.color }}>
                        {config.label}
                      </span>
                      {isSelected && <span className="checkmark">✓</span>}
                    </div>
                    <span className="item-description">{config.description}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </>
      )}

      <style jsx>{`
        .priority-dropdown-container {
          position: relative;
          display: inline-block;
        }

        .priority-button {
          display: flex;
          align-items: center;
          gap: 8px;
          background: white;
          border: 2px solid;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
          white-space: nowrap;
        }

        .priority-button:hover:not(.disabled) {
          opacity: 0.8;
          transform: translateY(-1px);
        }

        .priority-button.disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .priority-label {
          font-weight: 600;
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
          min-width: 240px;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
                      0 4px 6px -2px rgba(0, 0, 0, 0.05);
          z-index: 20;
          overflow: hidden;
        }

        .dropdown-item {
          display: block;
          width: 100%;
          padding: 12px 16px;
          background: white;
          border: none;
          border-left: 4px solid;
          text-align: left;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .dropdown-item:hover {
          background: #f9fafb;
        }

        .dropdown-item.selected {
          font-weight: 500;
        }

        .item-content {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .item-header {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .item-label {
          flex: 1;
          font-size: 14px;
          font-weight: 600;
        }

        .checkmark {
          font-weight: bold;
          font-size: 16px;
        }

        .item-description {
          font-size: 12px;
          color: #6b7280;
          margin-left: 24px;
        }
      `}</style>
    </div>
  );
};

export default PriorityDropdown;

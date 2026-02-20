/**
 * Task: T5.2.2 - TagChips Component
 * Spec Reference: phase5-spec.md Section 3.1.2
 * Constitution: constitution.md v5.0
 *
 * TagChips component for displaying and managing task tags.
 * Features:
 * - Display tags as colored chips
 * - Add new tags with autocomplete
 * - Remove tags with click
 * - Keyboard navigation
 * - Accessible with ARIA labels
 */

import React, { useState, useRef, useEffect } from 'react';
import { X, Plus, Tag } from 'lucide-react';

interface TagChipsProps {
  tags: string[];
  onTagsChange: (tags: string[]) => void;
  availableTags?: string[];
  maxTags?: number;
  editable?: boolean;
  colorScheme?: 'default' | 'colorful';
}

export const TagChips: React.FC<TagChipsProps> = ({
  tags,
  onTagsChange,
  availableTags = [],
  maxTags = 10,
  editable = true,
  colorScheme = 'colorful'
}) => {
  const [isAdding, setIsAdding] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isAdding && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isAdding]);

  useEffect(() => {
    if (inputValue.trim()) {
      const filtered = availableTags.filter(
        tag => tag.toLowerCase().includes(inputValue.toLowerCase()) &&
               !tags.includes(tag)
      );
      setSuggestions(filtered);
      setSelectedSuggestionIndex(-1);
    } else {
      setSuggestions([]);
    }
  }, [inputValue, availableTags, tags]);

  const handleAddTag = (tag: string) => {
    const trimmedTag = tag.trim();
    if (trimmedTag && !tags.includes(trimmedTag) && tags.length < maxTags) {
      onTagsChange([...tags, trimmedTag]);
      setInputValue('');
      setSuggestions([]);
      setIsAdding(false);
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    onTagsChange(tags.filter(tag => tag !== tagToRemove));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedSuggestionIndex >= 0 && suggestions[selectedSuggestionIndex]) {
        handleAddTag(suggestions[selectedSuggestionIndex]);
      } else if (inputValue.trim()) {
        handleAddTag(inputValue);
      }
    } else if (e.key === 'Escape') {
      setIsAdding(false);
      setInputValue('');
      setSuggestions([]);
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedSuggestionIndex(prev =>
        prev < suggestions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedSuggestionIndex(prev => prev > 0 ? prev - 1 : -1);
    }
  };

  const getTagColor = (tag: string, index: number) => {
    if (colorScheme === 'default') {
      return '#3b82f6';
    }

    const colors = [
      '#3b82f6', // blue
      '#10b981', // green
      '#f59e0b', // amber
      '#ef4444', // red
      '#8b5cf6', // violet
      '#ec4899', // pink
      '#06b6d4', // cyan
      '#f97316', // orange
    ];

    // Use tag name to consistently assign colors
    const hash = tag.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
  };

  return (
    <div className="tag-chips-container">
      <div className="tag-chips">
        {tags.map((tag, index) => (
          <div
            key={tag}
            className="tag-chip"
            style={{ backgroundColor: getTagColor(tag, index) }}
          >
            <Tag size={12} />
            <span>{tag}</span>
            {editable && (
              <button
                onClick={() => handleRemoveTag(tag)}
                className="remove-button"
                aria-label={`Remove tag ${tag}`}
              >
                <X size={12} />
              </button>
            )}
          </div>
        ))}

        {editable && tags.length < maxTags && (
          <>
            {isAdding ? (
              <div className="tag-input-container">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  onBlur={() => {
                    setTimeout(() => {
                      setIsAdding(false);
                      setInputValue('');
                      setSuggestions([]);
                    }, 200);
                  }}
                  placeholder="Add tag..."
                  className="tag-input"
                  maxLength={50}
                />
                {suggestions.length > 0 && (
                  <div className="suggestions-dropdown">
                    {suggestions.map((suggestion, index) => (
                      <button
                        key={suggestion}
                        onClick={() => handleAddTag(suggestion)}
                        className={`suggestion-item ${
                          index === selectedSuggestionIndex ? 'selected' : ''
                        }`}
                      >
                        <Tag size={14} />
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={() => setIsAdding(true)}
                className="add-tag-button"
                aria-label="Add tag"
              >
                <Plus size={14} />
                <span>Add tag</span>
              </button>
            )}
          </>
        )}
      </div>

      <style jsx>{`
        .tag-chips-container {
          width: 100%;
        }

        .tag-chips {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          align-items: center;
        }

        .tag-chip {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 6px 10px;
          background: #3b82f6;
          color: white;
          border-radius: 6px;
          font-size: 13px;
          font-weight: 500;
          transition: all 0.2s ease;
        }

        .tag-chip:hover {
          opacity: 0.9;
          transform: translateY(-1px);
        }

        .remove-button {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2px;
          background: rgba(255, 255, 255, 0.2);
          border: none;
          border-radius: 3px;
          color: white;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .remove-button:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .add-tag-button {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 6px 10px;
          background: white;
          border: 2px dashed #d1d5db;
          border-radius: 6px;
          font-size: 13px;
          color: #6b7280;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .add-tag-button:hover {
          border-color: #9ca3af;
          color: #374151;
        }

        .tag-input-container {
          position: relative;
        }

        .tag-input {
          padding: 6px 10px;
          border: 2px solid #3b82f6;
          border-radius: 6px;
          font-size: 13px;
          color: #1f2937;
          outline: none;
          min-width: 120px;
        }

        .suggestions-dropdown {
          position: absolute;
          top: calc(100% + 4px);
          left: 0;
          min-width: 200px;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
                      0 2px 4px -1px rgba(0, 0, 0, 0.06);
          z-index: 10;
          overflow: hidden;
        }

        .suggestion-item {
          display: flex;
          align-items: center;
          gap: 8px;
          width: 100%;
          padding: 10px 12px;
          background: white;
          border: none;
          text-align: left;
          font-size: 13px;
          color: #1f2937;
          cursor: pointer;
          transition: background 0.2s ease;
        }

        .suggestion-item:hover,
        .suggestion-item.selected {
          background: #f3f4f6;
        }
      `}</style>
    </div>
  );
};

export default TagChips;

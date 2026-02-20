/**
 * Task: T5.2.3 - SearchBar Component
 * Spec Reference: phase5-spec.md Section 3.1.3
 * Constitution: constitution.md v5.0
 *
 * SearchBar component with real-time search functionality.
 * Features:
 * - Real-time search as user types (with debounce)
 * - Clear button to reset search
 * - Keyboard shortcuts (Ctrl+K to focus)
 * - Accessible with ARIA labels
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Search, X } from 'lucide-react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  debounceMs?: number;
  initialValue?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = "Search tasks by title or description...",
  debounceMs = 300,
  initialValue = ""
}) => {
  const [searchQuery, setSearchQuery] = useState(initialValue);
  const [isFocused, setIsFocused] = useState(false);

  // Debounced search effect
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearch(searchQuery);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [searchQuery, debounceMs, onSearch]);

  // Keyboard shortcut: Ctrl+K to focus search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('task-search-input')?.focus();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleClear = useCallback(() => {
    setSearchQuery('');
    onSearch('');
  }, [onSearch]);

  return (
    <div className="search-bar-container">
      <div className={`search-bar ${isFocused ? 'focused' : ''}`}>
        <Search className="search-icon" size={20} />
        <input
          id="task-search-input"
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          aria-label="Search tasks"
          className="search-input"
        />
        {searchQuery && (
          <button
            onClick={handleClear}
            aria-label="Clear search"
            className="clear-button"
          >
            <X size={16} />
          </button>
        )}
        <kbd className="keyboard-hint">Ctrl+K</kbd>
      </div>

      <style jsx>{`
        .search-bar-container {
          width: 100%;
          max-width: 600px;
        }

        .search-bar {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 14px;
          background: white;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          transition: all 0.2s ease;
        }

        .search-bar.focused {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .search-icon {
          color: #6b7280;
          flex-shrink: 0;
        }

        .search-input {
          flex: 1;
          border: none;
          outline: none;
          font-size: 14px;
          color: #1f2937;
        }

        .search-input::placeholder {
          color: #9ca3af;
        }

        .clear-button {
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

        .clear-button:hover {
          background: #f3f4f6;
          color: #1f2937;
        }

        .keyboard-hint {
          display: none;
          padding: 2px 6px;
          background: #f3f4f6;
          border: 1px solid #e5e7eb;
          border-radius: 4px;
          font-size: 11px;
          color: #6b7280;
          font-family: monospace;
        }

        @media (min-width: 768px) {
          .keyboard-hint {
            display: block;
          }
        }
      `}</style>
    </div>
  );
};

export default SearchBar;

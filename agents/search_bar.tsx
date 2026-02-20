/**
 * Search Bar Component
 * Task: Frontend component for searching tasks
 * Spec Reference: phase5-spec.md Section 3.1.3 (Search)
 */
import React, { useState, useEffect } from 'react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/20/solid';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  delay?: number;
  className?: string;
}

const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = "Search tasks...",
  delay = 300,
  className = ''
}) => {
  const [query, setQuery] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Use debounce to delay search execution
  useEffect(() => {
    const handler = setTimeout(() => {
      onSearch(query);
      setIsTyping(false);
    }, delay);

    if (query) {
      setIsTyping(true);
    }

    return () => {
      clearTimeout(handler);
    };
  }, [query, delay, onSearch]);

  const clearSearch = () => {
    setQuery('');
    onSearch('');
  };

  return (
    <div className={`relative rounded-md shadow-sm ${className}`}>
      <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
        <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
      </div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        className="block w-full rounded-md border-0 py-1.5 pl-10 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
      />
      {query && (
        <button
          type="button"
          onClick={clearSearch}
          className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
        >
          <XMarkIcon className="h-5 w-5" aria-hidden="true" />
        </button>
      )}
      {isTyping && (
        <div className="absolute inset-y-0 right-8 flex items-center">
          <div className="h-5 w-5 border-t-2 border-blue-500 rounded-full animate-spin"></div>
        </div>
      )}
    </div>
  );
};

export default SearchBar;
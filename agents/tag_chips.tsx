/**
 * Tag Chips Component
 * Task: Frontend component for displaying and managing task tags
 * Spec Reference: phase5-spec.md Section 3.1.2 (Tags)
 */
import React from 'react';
import { XMarkIcon } from '@heroicons/react/20/solid';

interface TagChipProps {
  tag: string;
  onRemove?: (tag: string) => void;
  className?: string;
  removable?: boolean;
}

const TagChip: React.FC<TagChipProps> = ({
  tag,
  onRemove,
  className = '',
  removable = false
}) => {
  const handleRemove = () => {
    if (onRemove) {
      onRemove(tag);
    }
  };

  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium bg-blue-100 text-blue-800 ${className}`}>
      {tag}
      {removable && onRemove && (
        <button
          type="button"
          className="ml-2 flex-shrink-0 h-4 w-4 rounded-full inline-flex items-center justify-center text-blue-600 hover:bg-blue-200 hover:text-blue-800 focus:outline-none focus:bg-blue-500 focus:text-white"
          onClick={handleRemove}
          aria-label="Remove tag"
        >
          <XMarkIcon className="h-3 w-3" />
        </button>
      )}
    </span>
  );
};

interface TagChipsProps {
  tags: string[];
  onRemove?: (tag: string) => void;
  className?: string;
}

const TagChips: React.FC<TagChipsProps> = ({
  tags,
  onRemove,
  className = ''
}) => {
  if (!tags || tags.length === 0) {
    return null;
  }

  return (
    <div className={`flex flex-wrap gap-1 ${className}`}>
      {tags.map((tag) => (
        <TagChip
          key={tag}
          tag={tag}
          onRemove={onRemove}
          removable={!!onRemove}
        />
      ))}
    </div>
  );
};

interface TagInputProps {
  tags: string[];
  onAdd: (tag: string) => void;
  onRemove: (tag: string) => void;
  placeholder?: string;
  className?: string;
}

const TagInput: React.FC<TagInputProps> = ({
  tags,
  onAdd,
  onRemove,
  placeholder = "Add a tag...",
  className = ''
}) => {
  const [inputValue, setInputValue] = React.useState('');
  const inputRef = React.useRef<HTMLInputElement>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault();
      if (!tags.includes(inputValue.trim())) {
        onAdd(inputValue.trim());
      }
      setInputValue('');
    } else if (e.key === 'Backspace' && !inputValue && tags.length > 0) {
      // Remove last tag if input is empty and backspace is pressed
      onRemove(tags[tags.length - 1]);
    }
  };

  const handleAddClick = () => {
    if (inputValue.trim() && !tags.includes(inputValue.trim())) {
      onAdd(inputValue.trim());
      setInputValue('');
    }
  };

  return (
    <div className={`flex flex-wrap items-center gap-2 ${className}`}>
      <TagChips tags={tags} onRemove={onRemove} />
      <div className="flex-1 min-w-[120px]">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleInputKeyDown}
          placeholder={placeholder}
          className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-600 sm:text-sm sm:leading-6"
        />
        <button
          type="button"
          onClick={handleAddClick}
          className="mt-1 hidden sm:block rounded bg-blue-500 px-2 py-1 text-xs font-semibold text-white shadow-sm hover:bg-blue-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
        >
          Add
        </button>
      </div>
    </div>
  );
};

export { TagChip, TagChips, TagInput };
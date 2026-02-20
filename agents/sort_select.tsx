/**
 * Sort Select Component
 * Task: Frontend component for sorting tasks
 * Spec Reference: phase5-spec.md Section 3.1.5 (Sort)
 */
import React from 'react';
import { Listbox } from '@headlessui/react';
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/react/20/solid';

interface SortOption {
  value: string;
  label: string;
  icon?: React.ReactNode;
}

interface SortSelectProps {
  options: SortOption[];
  value: string;
  onChange: (value: string) => void;
  className?: string;
  direction?: 'asc' | 'desc';
  onDirectionChange?: (direction: 'asc' | 'desc') => void;
}

const SortSelect: React.FC<SortSelectProps> = ({
  options = [
    { value: 'created_at', label: 'Created Date' },
    { value: 'due_date', label: 'Due Date' },
    { value: 'priority', label: 'Priority' },
    { value: 'title', label: 'Title' }
  ],
  value,
  onChange,
  className = '',
  direction = 'desc',
  onDirectionChange
}) => {
  const currentOption = options.find(option => option.value === value) || options[0];

  const toggleDirection = () => {
    if (onDirectionChange) {
      onDirectionChange(direction === 'desc' ? 'asc' : 'desc');
    }
  };

  return (
    <div className={`relative ${className}`}>
      <Listbox value={value} onChange={onChange}>
        <div className="relative">
          <Listbox.Button className="relative w-full cursor-pointer rounded-md bg-white py-2 pl-3 pr-10 text-left shadow-sm ring-1 ring-inset ring-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:text-sm">
            <span className="block truncate">{currentOption?.label}</span>
            <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
              <ChevronUpDownIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
            </span>
          </Listbox.Button>
          <Listbox.Options className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
            {options.map((option) => (
              <Listbox.Option
                key={option.value}
                className={({ active }) =>
                  `relative cursor-pointer select-none py-2 pl-3 pr-9 ${
                    active ? 'bg-blue-600 text-white' : 'text-gray-900'
                  }`
                }
                value={option.value}
              >
                {({ selected, active }) => (
                  <>
                    <span className={`block truncate ${selected ? 'font-semibold' : 'font-normal'}`}>
                      {option.label}
                    </span>
                    {selected ? (
                      <span
                        className={`absolute inset-y-0 right-0 flex items-center pr-4 ${
                          active ? 'text-white' : 'text-blue-600'
                        }`}
                      >
                        <CheckIcon className="h-5 w-5" aria-hidden="true" />
                      </span>
                    ) : null}
                  </>
                )}
              </Listbox.Option>
            ))}
          </Listbox.Options>
        </div>
      </Listbox>

      {onDirectionChange && (
        <button
          type="button"
          onClick={toggleDirection}
          className={`ml-2 inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded shadow-sm ${
            direction === 'asc'
              ? 'bg-green-100 text-green-700 hover:bg-green-200'
              : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
          }`}
        >
          {direction === 'asc' ? '↑' : '↓'} {direction === 'asc' ? 'Asc' : 'Desc'}
        </button>
      )}
    </div>
  );
};

export default SortSelect;
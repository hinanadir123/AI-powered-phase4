/**
 * Priority Dropdown Component
 * Task: Frontend component for priority selection
 * Spec Reference: phase5-spec.md Section 3.1.1 (Priorities)
 */
import React, { useState } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { ChevronDownIcon } from '@heroicons/react/20/solid';

interface PriorityOption {
  value: string;
  label: string;
  color: string;
  bgColor: string;
}

interface PriorityDropdownProps {
  currentPriority: string;
  onChange: (priority: string) => void;
  className?: string;
}

const PriorityDropdown: React.FC<PriorityDropdownProps> = ({
  currentPriority,
  onChange,
  className = ''
}) => {
  const priorityOptions: PriorityOption[] = [
    {
      value: 'low',
      label: 'Low',
      color: 'text-gray-600',
      bgColor: 'bg-gray-100'
    },
    {
      value: 'medium',
      label: 'Medium',
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      value: 'high',
      label: 'High',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100'
    },
    {
      value: 'urgent',
      label: 'Urgent',
      color: 'text-red-600',
      bgColor: 'bg-red-100'
    }
  ];

  const currentOption = priorityOptions.find(option => option.value === currentPriority) || priorityOptions[1]; // Default to 'medium'

  return (
    <div className={`relative inline-block text-left ${className}`}>
      <Menu as="div" className="relative inline-block text-left">
        {({ open }) => (
          <>
            <div>
              <Menu.Button className={`inline-flex w-full justify-center gap-x-1.5 rounded-md px-3 py-2 text-sm font-semibold shadow-sm ring-1 ring-inset ring-gray-300 ${currentOption.color} ${currentOption.bgColor}`}>
                {currentOption.label}
                <ChevronDownIcon className="-mr-1 h-5 w-5" aria-hidden="true" />
              </Menu.Button>
            </div>

            <Transition
              show={open}
              as={Fragment}
              enter="transition ease-out duration-100"
              enterFrom="transform opacity-0 scale-95"
              enterTo="transform opacity-100 scale-100"
              leave="transition ease-in duration-75"
              leaveFrom="transform opacity-100 scale-100"
              leaveTo="transform opacity-0 scale-95"
            >
              <Menu.Items className="absolute right-0 z-10 mt-2 w-40 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                <div className="py-1">
                  {priorityOptions.map((option) => (
                    <Menu.Item key={option.value}>
                      {({ active }) => (
                        <button
                          onClick={() => onChange(option.value)}
                          className={`${
                            active ? 'bg-gray-100 text-gray-900' : 'text-gray-700'
                          } group flex items-center w-full px-4 py-2 text-sm`}
                        >
                          <span className={`inline-block w-3 h-3 rounded-full mr-2 ${option.bgColor}`}></span>
                          {option.label}
                        </button>
                      )}
                    </Menu.Item>
                  ))}
                </div>
              </Menu.Items>
            </Transition>
          </>
        )}
      </Menu>
    </div>
  );
};

export default PriorityDropdown;
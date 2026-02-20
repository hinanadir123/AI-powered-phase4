/**
 * Recurrence Configuration Modal Component
 * Task: Frontend component for setting up recurring tasks
 * Spec Reference: phase5-spec.md Section 3.2.1 (Recurring Tasks)
 */
import React, { useState } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface RecurrenceConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (config: RecurrenceConfig) => void;
  initialConfig?: RecurrenceConfig;
}

interface RecurrenceConfig {
  pattern: 'daily' | 'weekly' | 'monthly' | 'yearly';
  frequency: number;
  days?: string[]; // For weekly pattern
  day?: number; // For monthly pattern
  month?: number; // For yearly pattern
  endDate?: Date | null;
  cronExpression?: string;
  enabled: boolean;
}

const RecurrenceConfigModal: React.FC<RecurrenceConfigModalProps> = ({
  isOpen,
  onClose,
  onSave,
  initialConfig = {
    pattern: 'daily',
    frequency: 1,
    enabled: false
  }
}) => {
  const [config, setConfig] = useState<RecurrenceConfig>(initialConfig);

  const handleSave = () => {
    onSave(config);
    onClose();
  };

  const handleChange = (field: string, value: any) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  const handleDayToggle = (day: string) => {
    const currentDays = config.days || [];
    if (currentDays.includes(day)) {
      setConfig(prev => ({
        ...prev,
        days: currentDays.filter(d => d !== day)
      }));
    } else {
      setConfig(prev => ({
        ...prev,
        days: [...currentDays, day]
      }));
    }
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-10" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <Dialog.Title
                  as="h3"
                  className="text-lg font-medium leading-6 text-gray-900 flex justify-between items-center"
                >
                  Recurring Task Configuration
                  <button
                    type="button"
                    className="text-gray-400 hover:text-gray-500"
                    onClick={onClose}
                  >
                    <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                  </button>
                </Dialog.Title>

                <div className="mt-4 space-y-4">
                  <div className="flex items-center">
                    <input
                      id="recurrence-toggle"
                      type="checkbox"
                      checked={config.enabled}
                      onChange={(e) => handleChange('enabled', e.target.checked)}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <label htmlFor="recurrence-toggle" className="ml-2 block text-sm font-medium text-gray-900">
                      Enable recurrence
                    </label>
                  </div>

                  {config.enabled && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Pattern</label>
                        <select
                          value={config.pattern}
                          onChange={(e) => handleChange('pattern', e.target.value)}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        >
                          <option value="daily">Daily</option>
                          <option value="weekly">Weekly</option>
                          <option value="monthly">Monthly</option>
                          <option value="yearly">Yearly</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">Frequency</label>
                        <input
                          type="number"
                          min="1"
                          value={config.frequency}
                          onChange={(e) => handleChange('frequency', parseInt(e.target.value) || 1)}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        />
                      </div>

                      {config.pattern === 'weekly' && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Repeat on</label>
                          <div className="mt-2 grid grid-cols-4 gap-2">
                            {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map(day => (
                              <button
                                key={day}
                                type="button"
                                onClick={() => handleDayToggle(day)}
                                className={`py-2 px-3 text-sm rounded-md ${
                                  (config.days || []).includes(day)
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                                }`}
                              >
                                {day.slice(0, 3)}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}

                      {config.pattern === 'monthly' && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700">Day of month</label>
                          <input
                            type="number"
                            min="1"
                            max="31"
                            value={config.day || 1}
                            onChange={(e) => handleChange('day', parseInt(e.target.value) || 1)}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                          />
                        </div>
                      )}

                      {config.pattern === 'yearly' && (
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700">Day of month</label>
                            <input
                              type="number"
                              min="1"
                              max="31"
                              value={config.day || 1}
                              onChange={(e) => handleChange('day', parseInt(e.target.value) || 1)}
                              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700">Month</label>
                            <select
                              value={config.month || 1}
                              onChange={(e) => handleChange('month', parseInt(e.target.value))}
                              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                            >
                              {Array.from({ length: 12 }, (_, i) => (
                                <option key={i + 1} value={i + 1}>
                                  {new Date(0, i).toLocaleString('default', { month: 'long' })}
                                </option>
                              ))}
                            </select>
                          </div>
                        </div>
                      )}

                      <div>
                        <label className="block text-sm font-medium text-gray-700">End date (optional)</label>
                        <input
                          type="date"
                          value={config.endDate ? config.endDate.toISOString().split('T')[0] : ''}
                          onChange={(e) => handleChange('endDate', e.target.value ? new Date(e.target.value) : null)}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        />
                      </div>
                    </>
                  )}
                </div>

                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    type="button"
                    className="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onClick={onClose}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onClick={handleSave}
                  >
                    Save
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default RecurrenceConfigModal;
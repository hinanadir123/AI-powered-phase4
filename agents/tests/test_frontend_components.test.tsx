// Task: T5.3.6 - Unit Tests for Frontend Components
// Spec Reference: phase5-spec.md Section 3.2 (Advanced Features)
// Constitution: constitution.md v5.0 Section 10.1 (Code Validation)
//
// Comprehensive unit tests for:
// - RecurrenceModal component
// - DueDatePicker component
// - ReminderConfig component
// - TaskDueDateIndicator component
//
// Version: 1.0
// Date: 2026-02-15

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import RecurrenceModal from '../RecurrenceModal';
import DueDatePicker from '../DueDatePicker';
import ReminderConfigModal from '../ReminderConfig';
import TaskDueDateIndicator from '../TaskDueDateIndicator';

describe('RecurrenceModal', () => {
  const mockOnClose = jest.fn();
  const mockOnSave = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders modal when open', () => {
    render(
      <RecurrenceModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    expect(screen.getByText('Configure Recurrence')).toBeInTheDocument();
    expect(screen.getByLabelText('Enable recurrence')).toBeInTheDocument();
  });

  test('does not render when closed', () => {
    render(
      <RecurrenceModal
        open={false}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    expect(screen.queryByText('Configure Recurrence')).not.toBeInTheDocument();
  });

  test('allows selecting daily interval', async () => {
    render(
      <RecurrenceModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const dailyRadio = screen.getByLabelText('Daily');
    fireEvent.click(dailyRadio);

    expect(dailyRadio).toBeChecked();
  });

  test('allows selecting weekly interval with days', async () => {
    render(
      <RecurrenceModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const weeklyRadio = screen.getByLabelText('Weekly');
    fireEvent.click(weeklyRadio);

    const mondayCheckbox = screen.getByLabelText(/Mon/i);
    fireEvent.click(mondayCheckbox);

    expect(mondayCheckbox).toBeChecked();
  });

  test('validates weekly recurrence requires at least one day', async () => {
    render(
      <RecurrenceModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const weeklyRadio = screen.getByLabelText('Weekly');
    fireEvent.click(weeklyRadio);

    // Uncheck all days (if any are checked by default)
    const checkboxes = screen.getAllByRole('checkbox');
    checkboxes.forEach(cb => {
      if (cb.getAttribute('aria-label')?.match(/Mon|Tue|Wed|Thu|Fri|Sat|Sun/)) {
        if ((cb as HTMLInputElement).checked) {
          fireEvent.click(cb);
        }
      }
    });

    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText(/select at least one day/i)).toBeInTheDocument();
    });

    expect(mockOnSave).not.toHaveBeenCalled();
  });

  test('calls onSave with correct config', async () => {
    render(
      <RecurrenceModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
      />
    );

    const weeklyRadio = screen.getByLabelText('Weekly');
    fireEvent.click(weeklyRadio);

    const mondayCheckbox = screen.getByLabelText(/Mon/i);
    fireEvent.click(mondayCheckbox);

    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(mockOnSave).toHaveBeenCalledWith(
        expect.objectContaining({
          enabled: true,
          interval: 'weekly',
          frequency: 1,
          days: expect.arrayContaining(['monday'])
        })
      );
    });
  });

  test('initializes with existing config', () => {
    const initialConfig = {
      enabled: true,
      interval: 'daily' as const,
      frequency: 2,
      days: undefined,
      end_date: null
    };

    render(
      <RecurrenceModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        initialConfig={initialConfig}
      />
    );

    const dailyRadio = screen.getByLabelText('Daily');
    expect(dailyRadio).toBeChecked();

    const frequencyInput = screen.getByLabelText('Frequency');
    expect(frequencyInput).toHaveValue(2);
  });
});

describe('DueDatePicker', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders date picker', () => {
    render(
      <DueDatePicker
        value={null}
        onChange={mockOnChange}
      />
    );

    expect(screen.getByLabelText('Due Date')).toBeInTheDocument();
  });

  test('displays quick action buttons', () => {
    render(
      <DueDatePicker
        value={null}
        onChange={mockOnChange}
        showQuickActions={true}
      />
    );

    expect(screen.getByText('Today')).toBeInTheDocument();
    expect(screen.getByText('Tomorrow')).toBeInTheDocument();
    expect(screen.getByText('Next Week')).toBeInTheDocument();
  });

  test('calls onChange when quick action clicked', async () => {
    render(
      <DueDatePicker
        value={null}
        onChange={mockOnChange}
        showQuickActions={true}
      />
    );

    const todayButton = screen.getByText('Today');
    fireEvent.click(todayButton);

    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalled();
    });
  });

  test('shows overdue warning for past dates', () => {
    const pastDate = new Date('2020-01-01');

    render(
      <DueDatePicker
        value={pastDate}
        onChange={mockOnChange}
      />
    );

    expect(screen.getByText(/in the past/i)).toBeInTheDocument();
  });

  test('displays clear button when date is set', () => {
    const futureDate = new Date('2026-12-31');

    render(
      <DueDatePicker
        value={futureDate}
        onChange={mockOnChange}
        showQuickActions={true}
      />
    );

    expect(screen.getByText('Clear')).toBeInTheDocument();
  });
});

describe('ReminderConfigModal', () => {
  const mockOnClose = jest.fn();
  const mockOnSave = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders modal when open', () => {
    render(
      <ReminderConfigModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        dueDate={new Date('2026-12-31')}
      />
    );

    expect(screen.getByText('Configure Reminder')).toBeInTheDocument();
  });

  test('shows warning when no due date', () => {
    render(
      <ReminderConfigModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        dueDate={null}
      />
    );

    expect(screen.getByText(/no due date set/i)).toBeInTheDocument();
  });

  test('allows selecting time before options', () => {
    render(
      <ReminderConfigModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        dueDate={new Date('2026-12-31')}
      />
    );

    const oneHourRadio = screen.getByLabelText('1 hour before');
    fireEvent.click(oneHourRadio);

    expect(oneHourRadio).toBeChecked();
  });

  test('allows selecting notification channels', () => {
    render(
      <ReminderConfigModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        dueDate={new Date('2026-12-31')}
      />
    );

    const emailCheckbox = screen.getByLabelText('Email');
    const pushCheckbox = screen.getByLabelText('Push Notification');

    fireEvent.click(emailCheckbox);
    fireEvent.click(pushCheckbox);

    expect(emailCheckbox).toBeChecked();
    expect(pushCheckbox).toBeChecked();
  });

  test('validates at least one channel is selected', async () => {
    render(
      <ReminderConfigModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        dueDate={new Date('2026-12-31')}
      />
    );

    // Uncheck all channels
    const checkboxes = screen.getAllByRole('checkbox');
    checkboxes.forEach(cb => {
      if ((cb as HTMLInputElement).checked) {
        fireEvent.click(cb);
      }
    });

    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText(/select at least one notification channel/i)).toBeInTheDocument();
    });

    expect(mockOnSave).not.toHaveBeenCalled();
  });

  test('calls onSave with correct config', async () => {
    render(
      <ReminderConfigModal
        open={true}
        onClose={mockOnClose}
        onSave={mockOnSave}
        dueDate={new Date('2026-12-31')}
      />
    );

    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(mockOnSave).toHaveBeenCalledWith(
        expect.objectContaining({
          enabled: true,
          time_before: expect.any(String),
          channels: expect.any(Array)
        })
      );
    });
  });
});

describe('TaskDueDateIndicator', () => {
  test('renders nothing when no due date', () => {
    const { container } = render(
      <TaskDueDateIndicator
        dueDate={null}
        status="pending"
      />
    );

    expect(container.firstChild).toBeNull();
  });

  test('shows overdue indicator for past dates', () => {
    const pastDate = new Date('2020-01-01');

    render(
      <TaskDueDateIndicator
        dueDate={pastDate}
        status="pending"
      />
    );

    expect(screen.getByText(/overdue/i)).toBeInTheDocument();
  });

  test('shows completed indicator for completed tasks', () => {
    const futureDate = new Date('2026-12-31');

    render(
      <TaskDueDateIndicator
        dueDate={futureDate}
        status="completed"
      />
    );

    expect(screen.getByText('Completed')).toBeInTheDocument();
  });

  test('shows recurring icon when task is recurring', () => {
    const futureDate = new Date('2026-12-31');

    render(
      <TaskDueDateIndicator
        dueDate={futureDate}
        status="pending"
        isRecurring={true}
      />
    );

    // Check for recurring icon tooltip
    const recurringIcon = screen.getByTitle('Recurring task');
    expect(recurringIcon).toBeInTheDocument();
  });

  test('applies correct color for urgent tasks', () => {
    const urgentDate = new Date(Date.now() + 12 * 60 * 60 * 1000); // 12 hours from now

    const { container } = render(
      <TaskDueDateIndicator
        dueDate={urgentDate}
        status="pending"
      />
    );

    // Check for error color class (MUI applies specific classes)
    const chip = container.querySelector('.MuiChip-colorError');
    expect(chip).toBeInTheDocument();
  });
});

// Integration test
describe('Advanced Features Integration', () => {
  test('complete workflow: set due date, configure reminder, set recurrence', async () => {
    const mockOnDueDateChange = jest.fn();
    const mockOnReminderSave = jest.fn();
    const mockOnRecurrenceSave = jest.fn();

    const { rerender } = render(
      <div>
        <DueDatePicker
          value={null}
          onChange={mockOnDueDateChange}
        />
      </div>
    );

    // Step 1: Set due date
    const todayButton = screen.getByText('Today');
    fireEvent.click(todayButton);

    await waitFor(() => {
      expect(mockOnDueDateChange).toHaveBeenCalled();
    });

    // Step 2: Configure reminder (with due date set)
    const dueDate = new Date('2026-12-31');
    rerender(
      <div>
        <ReminderConfigModal
          open={true}
          onClose={() => {}}
          onSave={mockOnReminderSave}
          dueDate={dueDate}
        />
      </div>
    );

    const reminderSaveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(reminderSaveButton);

    await waitFor(() => {
      expect(mockOnReminderSave).toHaveBeenCalled();
    });

    // Step 3: Configure recurrence
    rerender(
      <div>
        <RecurrenceModal
          open={true}
          onClose={() => {}}
          onSave={mockOnRecurrenceSave}
        />
      </div>
    );

    const weeklyRadio = screen.getByLabelText('Weekly');
    fireEvent.click(weeklyRadio);

    const recurrenceSaveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(recurrenceSaveButton);

    await waitFor(() => {
      expect(mockOnRecurrenceSave).toHaveBeenCalled();
    });
  });
});

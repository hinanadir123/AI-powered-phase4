// Task: T5.3.6 - DueDatePicker Component
// Spec Reference: phase5-spec.md Section 3.2.2 (Due Dates & Reminders)
// Constitution: constitution.md v5.0 Section 4.4
//
// Date/time picker component for setting task due dates with:
// - Calendar date selection
// - Time selection
// - Visual indicators for overdue tasks
// - Quick date shortcuts (today, tomorrow, next week)
//
// Version: 1.0
// Date: 2026-02-15

import React, { useState } from 'react';
import {
  Box,
  Button,
  ButtonGroup,
  TextField,
  Typography,
  Chip,
  Stack
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import {
  addDays,
  addWeeks,
  startOfDay,
  endOfDay,
  setHours,
  setMinutes,
  isPast,
  formatDistanceToNow
} from 'date-fns';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import WarningIcon from '@mui/icons-material/Warning';

interface DueDatePickerProps {
  value: Date | null;
  onChange: (date: Date | null) => void;
  label?: string;
  helperText?: string;
  showQuickActions?: boolean;
  minDate?: Date;
}

export const DueDatePicker: React.FC<DueDatePickerProps> = ({
  value,
  onChange,
  label = 'Due Date',
  helperText,
  showQuickActions = true,
  minDate = new Date()
}) => {
  const [selectedDate, setSelectedDate] = useState<Date | null>(value);

  const handleDateChange = (newDate: Date | null) => {
    setSelectedDate(newDate);
    onChange(newDate);
  };

  const setQuickDate = (date: Date) => {
    handleDateChange(date);
  };

  const quickActions = [
    {
      label: 'Today',
      date: setHours(setMinutes(endOfDay(new Date()), 0), 23)
    },
    {
      label: 'Tomorrow',
      date: setHours(setMinutes(endOfDay(addDays(new Date(), 1)), 0), 23)
    },
    {
      label: 'Next Week',
      date: setHours(setMinutes(endOfDay(addWeeks(new Date(), 1)), 0), 23)
    }
  ];

  const isOverdue = selectedDate && isPast(selectedDate);
  const timeUntilDue = selectedDate ? formatDistanceToNow(selectedDate, { addSuffix: true }) : null;

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ width: '100%' }}>
        <DateTimePicker
          label={label}
          value={selectedDate}
          onChange={handleDateChange}
          minDate={minDate}
          slotProps={{
            textField: {
              fullWidth: true,
              helperText: helperText || (isOverdue ? 'This date is in the past' : timeUntilDue),
              error: isOverdue,
              InputProps: {
                startAdornment: isOverdue ? (
                  <WarningIcon color="error" sx={{ mr: 1 }} />
                ) : (
                  <AccessTimeIcon color="action" sx={{ mr: 1 }} />
                )
              }
            }
          }}
        />

        {showQuickActions && (
          <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
            <Typography variant="caption" sx={{ alignSelf: 'center', mr: 1 }}>
              Quick:
            </Typography>
            {quickActions.map((action) => (
              <Button
                key={action.label}
                size="small"
                variant="outlined"
                onClick={() => setQuickDate(action.date)}
              >
                {action.label}
              </Button>
            ))}
            {selectedDate && (
              <Button
                size="small"
                variant="outlined"
                color="error"
                onClick={() => handleDateChange(null)}
              >
                Clear
              </Button>
            )}
          </Stack>
        )}

        {selectedDate && (
          <Box sx={{ mt: 2 }}>
            <Chip
              label={`Due ${timeUntilDue}`}
              color={isOverdue ? 'error' : 'primary'}
              size="small"
              icon={isOverdue ? <WarningIcon /> : <AccessTimeIcon />}
            />
          </Box>
        )}
      </Box>
    </LocalizationProvider>
  );
};

export default DueDatePicker;

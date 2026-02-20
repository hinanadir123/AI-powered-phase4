// Task: T5.3.6 - RecurrenceModal Component
// Spec Reference: phase5-spec.md Section 3.2.1 (Recurring Tasks)
// Constitution: constitution.md v5.0 Section 4.4
//
// Modal component for configuring task recurrence with:
// - Interval selection (daily, weekly, monthly, custom)
// - Frequency input
// - Day selection for weekly recurrence
// - End date picker
//
// Version: 1.0
// Date: 2026-02-15

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField,
  Checkbox,
  FormGroup,
  Box,
  Typography,
  Alert
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

interface RecurrenceConfig {
  enabled: boolean;
  interval: 'daily' | 'weekly' | 'monthly' | 'custom';
  frequency: number;
  days?: string[];
  end_date?: Date | null;
}

interface RecurrenceModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (config: RecurrenceConfig) => void;
  initialConfig?: RecurrenceConfig;
}

const WEEKDAYS = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday'
];

export const RecurrenceModal: React.FC<RecurrenceModalProps> = ({
  open,
  onClose,
  onSave,
  initialConfig
}) => {
  const [enabled, setEnabled] = useState(true);
  const [interval, setInterval] = useState<'daily' | 'weekly' | 'monthly' | 'custom'>('weekly');
  const [frequency, setFrequency] = useState(1);
  const [selectedDays, setSelectedDays] = useState<string[]>(['monday']);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [error, setError] = useState<string>('');

  // Initialize form with existing config
  useEffect(() => {
    if (initialConfig) {
      setEnabled(initialConfig.enabled);
      setInterval(initialConfig.interval);
      setFrequency(initialConfig.frequency);
      setSelectedDays(initialConfig.days || ['monday']);
      setEndDate(initialConfig.end_date || null);
    }
  }, [initialConfig]);

  const handleDayToggle = (day: string) => {
    setSelectedDays(prev => {
      if (prev.includes(day)) {
        return prev.filter(d => d !== day);
      } else {
        return [...prev, day];
      }
    });
  };

  const handleSave = () => {
    // Validation
    if (interval === 'weekly' && selectedDays.length === 0) {
      setError('Please select at least one day for weekly recurrence');
      return;
    }

    if (frequency < 1 || frequency > 365) {
      setError('Frequency must be between 1 and 365');
      return;
    }

    const config: RecurrenceConfig = {
      enabled,
      interval,
      frequency,
      days: interval === 'weekly' ? selectedDays : undefined,
      end_date: endDate
    };

    onSave(config);
    onClose();
  };

  const getRecurrenceSummary = () => {
    if (!enabled) return 'Recurrence disabled';

    let summary = `Repeats every ${frequency} ${interval}`;
    if (interval === 'weekly' && selectedDays.length > 0) {
      summary += ` on ${selectedDays.join(', ')}`;
    }
    if (endDate) {
      summary += ` until ${endDate.toLocaleDateString()}`;
    }
    return summary;
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Configure Recurrence</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 2 }}>
          {/* Enable/Disable Toggle */}
          <FormControlLabel
            control={
              <Checkbox
                checked={enabled}
                onChange={(e) => setEnabled(e.target.checked)}
              />
            }
            label="Enable recurrence"
          />

          {enabled && (
            <>
              {/* Interval Selection */}
              <FormControl component="fieldset">
                <FormLabel component="legend">Repeat Interval</FormLabel>
                <RadioGroup
                  value={interval}
                  onChange={(e) => setInterval(e.target.value as any)}
                >
                  <FormControlLabel value="daily" control={<Radio />} label="Daily" />
                  <FormControlLabel value="weekly" control={<Radio />} label="Weekly" />
                  <FormControlLabel value="monthly" control={<Radio />} label="Monthly" />
                  <FormControlLabel value="custom" control={<Radio />} label="Custom" />
                </RadioGroup>
              </FormControl>

              {/* Frequency Input */}
              <TextField
                label="Frequency"
                type="number"
                value={frequency}
                onChange={(e) => setFrequency(parseInt(e.target.value) || 1)}
                inputProps={{ min: 1, max: 365 }}
                helperText={`Repeat every ${frequency} ${interval}(s)`}
                fullWidth
              />

              {/* Day Selection for Weekly */}
              {interval === 'weekly' && (
                <FormControl component="fieldset">
                  <FormLabel component="legend">Repeat On</FormLabel>
                  <FormGroup row>
                    {WEEKDAYS.map(day => (
                      <FormControlLabel
                        key={day}
                        control={
                          <Checkbox
                            checked={selectedDays.includes(day)}
                            onChange={() => handleDayToggle(day)}
                          />
                        }
                        label={day.charAt(0).toUpperCase() + day.slice(1, 3)}
                      />
                    ))}
                  </FormGroup>
                </FormControl>
              )}

              {/* End Date Picker */}
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="End Date (Optional)"
                  value={endDate}
                  onChange={(newValue) => setEndDate(newValue)}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      helperText: 'Leave empty for no end date'
                    }
                  }}
                />
              </LocalizationProvider>

              {/* Summary */}
              <Alert severity="info">
                <Typography variant="body2">
                  {getRecurrenceSummary()}
                </Typography>
              </Alert>
            </>
          )}

          {/* Error Message */}
          {error && (
            <Alert severity="error" onClose={() => setError('')}>
              {error}
            </Alert>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave} variant="contained" color="primary">
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RecurrenceModal;

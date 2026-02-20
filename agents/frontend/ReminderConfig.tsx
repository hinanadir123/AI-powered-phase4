// Task: T5.3.6 - ReminderConfig Component
// Spec Reference: phase5-spec.md Section 3.2.2 (Due Dates & Reminders)
// Constitution: constitution.md v5.0 Section 4.4
//
// Modal component for configuring task reminders with:
// - Enable/disable toggle
// - Time before due date selection
// - Notification channel selection (email, push, in-app)
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
  Checkbox,
  FormGroup,
  Box,
  Typography,
  Alert,
  Chip,
  Stack
} from '@mui/material';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import EmailIcon from '@mui/icons-material/Email';
import PhoneAndroidIcon from '@mui/icons-material/PhoneAndroid';
import NotificationsIcon from '@mui/icons-material/Notifications';

interface ReminderConfig {
  enabled: boolean;
  time_before: string;
  channels: string[];
}

interface ReminderConfigProps {
  open: boolean;
  onClose: () => void;
  onSave: (config: ReminderConfig) => void;
  initialConfig?: ReminderConfig;
  dueDate?: Date | null;
}

const TIME_OPTIONS = [
  { value: '15m', label: '15 minutes before' },
  { value: '30m', label: '30 minutes before' },
  { value: '1h', label: '1 hour before' },
  { value: '2h', label: '2 hours before' },
  { value: '1d', label: '1 day before' },
  { value: '1w', label: '1 week before' }
];

const CHANNEL_OPTIONS = [
  { value: 'email', label: 'Email', icon: <EmailIcon /> },
  { value: 'push', label: 'Push Notification', icon: <PhoneAndroidIcon /> },
  { value: 'in-app', label: 'In-App', icon: <NotificationsIcon /> }
];

export const ReminderConfigModal: React.FC<ReminderConfigProps> = ({
  open,
  onClose,
  onSave,
  initialConfig,
  dueDate
}) => {
  const [enabled, setEnabled] = useState(true);
  const [timeBefore, setTimeBefore] = useState('1h');
  const [channels, setChannels] = useState<string[]>(['email']);
  const [error, setError] = useState<string>('');

  // Initialize form with existing config
  useEffect(() => {
    if (initialConfig) {
      setEnabled(initialConfig.enabled);
      setTimeBefore(initialConfig.time_before);
      setChannels(initialConfig.channels);
    }
  }, [initialConfig]);

  const handleChannelToggle = (channel: string) => {
    setChannels(prev => {
      if (prev.includes(channel)) {
        return prev.filter(c => c !== channel);
      } else {
        return [...prev, channel];
      }
    });
  };

  const handleSave = () => {
    // Validation
    if (!dueDate) {
      setError('Cannot set reminder without a due date. Please set a due date first.');
      return;
    }

    if (enabled && channels.length === 0) {
      setError('Please select at least one notification channel');
      return;
    }

    const config: ReminderConfig = {
      enabled,
      time_before: timeBefore,
      channels
    };

    onSave(config);
    onClose();
  };

  const getReminderSummary = () => {
    if (!enabled) return 'Reminders disabled';

    const timeLabel = TIME_OPTIONS.find(opt => opt.value === timeBefore)?.label || timeBefore;
    const channelLabels = channels.map(ch =>
      CHANNEL_OPTIONS.find(opt => opt.value === ch)?.label || ch
    ).join(', ');

    return `Remind ${timeLabel} via ${channelLabels}`;
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <NotificationsActiveIcon />
          Configure Reminder
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 2 }}>
          {/* Due Date Warning */}
          {!dueDate && (
            <Alert severity="warning">
              No due date set. Please set a due date before configuring reminders.
            </Alert>
          )}

          {/* Enable/Disable Toggle */}
          <FormControlLabel
            control={
              <Checkbox
                checked={enabled}
                onChange={(e) => setEnabled(e.target.checked)}
                disabled={!dueDate}
              />
            }
            label="Enable reminder"
          />

          {enabled && dueDate && (
            <>
              {/* Time Before Selection */}
              <FormControl component="fieldset">
                <FormLabel component="legend">Remind Me</FormLabel>
                <RadioGroup
                  value={timeBefore}
                  onChange={(e) => setTimeBefore(e.target.value)}
                >
                  {TIME_OPTIONS.map(option => (
                    <FormControlLabel
                      key={option.value}
                      value={option.value}
                      control={<Radio />}
                      label={option.label}
                    />
                  ))}
                </RadioGroup>
              </FormControl>

              {/* Channel Selection */}
              <FormControl component="fieldset">
                <FormLabel component="legend">Notification Channels</FormLabel>
                <FormGroup>
                  {CHANNEL_OPTIONS.map(option => (
                    <FormControlLabel
                      key={option.value}
                      control={
                        <Checkbox
                          checked={channels.includes(option.value)}
                          onChange={() => handleChannelToggle(option.value)}
                          icon={option.icon}
                          checkedIcon={option.icon}
                        />
                      }
                      label={option.label}
                    />
                  ))}
                </FormGroup>
              </FormControl>

              {/* Summary */}
              <Alert severity="info">
                <Typography variant="body2">
                  {getReminderSummary()}
                </Typography>
              </Alert>

              {/* Selected Channels Display */}
              {channels.length > 0 && (
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Selected Channels:
                  </Typography>
                  <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                    {channels.map(channel => {
                      const option = CHANNEL_OPTIONS.find(opt => opt.value === channel);
                      return (
                        <Chip
                          key={channel}
                          label={option?.label}
                          icon={option?.icon}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      );
                    })}
                  </Stack>
                </Box>
              )}
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
        <Button
          onClick={handleSave}
          variant="contained"
          color="primary"
          disabled={!dueDate}
        >
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ReminderConfigModal;

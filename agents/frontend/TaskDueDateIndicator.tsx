// Task: T5.3.6 - TaskDueDateIndicator Component
// Spec Reference: phase5-spec.md Section 3.2.2 (Visual indicators for due dates)
// Constitution: constitution.md v5.0 Section 4.4
//
// Visual indicator component that displays task due date status with:
// - Color coding (red for overdue, yellow for due soon, green for on track)
// - Icons and badges
// - Relative time display
//
// Version: 1.0
// Date: 2026-02-15

import React from 'react';
import {
  Box,
  Chip,
  Tooltip,
  Typography
} from '@mui/material';
import {
  Warning as WarningIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  Repeat as RepeatIcon
} from '@mui/icons-material';
import { formatDistanceToNow, isPast, differenceInHours, differenceInDays } from 'date-fns';

interface TaskDueDateIndicatorProps {
  dueDate: Date | null;
  status: 'pending' | 'in-progress' | 'completed';
  isRecurring?: boolean;
  size?: 'small' | 'medium';
}

export const TaskDueDateIndicator: React.FC<TaskDueDateIndicatorProps> = ({
  dueDate,
  status,
  isRecurring = false,
  size = 'medium'
}) => {
  if (!dueDate) {
    return null;
  }

  const now = new Date();
  const isOverdue = isPast(dueDate) && status !== 'completed';
  const hoursUntilDue = differenceInHours(dueDate, now);
  const daysUntilDue = differenceInDays(dueDate, now);

  // Determine urgency level
  let urgency: 'overdue' | 'urgent' | 'soon' | 'normal' = 'normal';
  let color: 'error' | 'warning' | 'success' | 'default' = 'default';
  let icon = <ScheduleIcon />;

  if (status === 'completed') {
    urgency = 'normal';
    color = 'success';
    icon = <CheckCircleIcon />;
  } else if (isOverdue) {
    urgency = 'overdue';
    color = 'error';
    icon = <WarningIcon />;
  } else if (hoursUntilDue <= 24) {
    urgency = 'urgent';
    color = 'error';
    icon = <WarningIcon />;
  } else if (daysUntilDue <= 3) {
    urgency = 'soon';
    color = 'warning';
    icon = <ScheduleIcon />;
  }

  const getLabel = () => {
    if (status === 'completed') {
      return 'Completed';
    }
    if (isOverdue) {
      return `Overdue ${formatDistanceToNow(dueDate, { addSuffix: true })}`;
    }
    return `Due ${formatDistanceToNow(dueDate, { addSuffix: true })}`;
  };

  const getTooltip = () => {
    const dateStr = dueDate.toLocaleString();
    if (isOverdue) {
      return `Overdue! Was due on ${dateStr}`;
    }
    return `Due on ${dateStr}`;
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Tooltip title={getTooltip()} arrow>
        <Chip
          icon={icon}
          label={getLabel()}
          color={color}
          size={size}
          variant={isOverdue ? 'filled' : 'outlined'}
          sx={{
            fontWeight: isOverdue ? 'bold' : 'normal',
            animation: isOverdue ? 'pulse 2s infinite' : 'none',
            '@keyframes pulse': {
              '0%, 100%': { opacity: 1 },
              '50%': { opacity: 0.7 }
            }
          }}
        />
      </Tooltip>

      {isRecurring && (
        <Tooltip title="Recurring task" arrow>
          <RepeatIcon color="primary" fontSize="small" />
        </Tooltip>
      )}
    </Box>
  );
};

export default TaskDueDateIndicator;

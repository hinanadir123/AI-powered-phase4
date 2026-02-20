// React component for displaying tasks with Phase 5 features

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Paper,
  Chip,
  Divider,
  CircularProgress,
  Alert,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import { Task, PriorityLevel } from '../../types/task';
import apiService from '../../services/api';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

interface TaskListProps {
  userId: string;
}

const TaskList: React.FC<TaskListProps> = ({ userId }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [availableTags, setAvailableTags] = useState<string[]>([]);

  // Phase 5: Search, filter, and sort state
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState<string>('created_at:desc');

  useEffect(() => {
    fetchTasks();
    fetchTags();
  }, [userId, searchQuery, statusFilter, priorityFilter, sortBy]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const tasksData = await apiService.getTasks(userId, {
        status: statusFilter,
        priority: priorityFilter || undefined,
        search: searchQuery || undefined,
        sort: sortBy
      });
      setTasks(tasksData);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch tasks';
      setError(errorMessage);
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTags = async () => {
    try {
      const tags = await apiService.getTags(userId);
      setAvailableTags(tags.map(t => t.name));
    } catch (err) {
      console.error('Failed to fetch tags:', err);
    }
  };

  const handleToggleTask = async (task: Task) => {
    try {
      if (!task.completed) {
        // If task has recurrence, use the complete-recurring endpoint
        if (task.recurrence_pattern) {
          const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001'}/api/${userId}/tasks/${task.id}/complete-recurring`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
          });

          if (response.ok) {
            const updatedTask = await response.json();
            setTasks(prevTasks => prevTasks.map(t => t.id === task.id ? updatedTask : t));
            // Refresh to show new recurring instance
            fetchTasks();
          }
        } else {
          const updatedTask = await apiService.completeTask(userId, task.id);
          setTasks(prevTasks => prevTasks.map(t => t.id === task.id ? updatedTask : t));
        }
      } else {
        const updatedTask = await apiService.updateTask(userId, task.id, { completed: false });
        setTasks(prevTasks => prevTasks.map(t => t.id === task.id ? updatedTask : t));
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update task';
      setError(errorMessage);
      console.error('Error updating task:', err);
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      await apiService.deleteTask(userId, taskId);
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete task';
      setError(errorMessage);
      console.error('Error deleting task:', err);
    }
  };

  const handlePriorityChange = async (taskId: number, priority: PriorityLevel) => {
    try {
      const updatedTask = await apiService.updateTask(userId, taskId, { priority });
      setTasks(prevTasks => prevTasks.map(t => t.id === taskId ? updatedTask : t));
    } catch (err) {
      console.error('Failed to update priority:', err);
    }
  };

  const getPriorityColor = (priority: PriorityLevel) => {
    const colors = {
      low: '#10b981',
      medium: '#f59e0b',
      high: '#ef4444',
      urgent: '#dc2626'
    };
    return colors[priority] || colors.medium;
  };

  const isOverdue = (task: Task) => {
    if (!task.due_date || task.completed) return false;
    return new Date(task.due_date) < new Date();
  };

  const formatDueDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays < 0) {
      return `Overdue by ${Math.abs(diffDays)} day(s)`;
    } else if (diffDays === 0) {
      return 'Due today';
    } else if (diffDays === 1) {
      return 'Due tomorrow';
    } else {
      return `Due in ${diffDays} day(s)`;
    }
  };

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <CircularProgress />
        <Typography>Loading tasks...</Typography>
      </Box>
    );
  }

  const pendingTasks = tasks.filter(task => !task.completed);
  const completedTasks = tasks.filter(task => task.completed);

  return (
    <Box sx={{ width: '100%', height: '100%', overflow: 'auto', p: 1 }}>
      <Typography variant="h6" gutterBottom>
        My Tasks
      </Typography>

      {/* Phase 5: Search and Filters */}
      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search tasks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 1 }}
        />

        <Box sx={{ display: 'flex', gap: 1 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={statusFilter}
              label="Status"
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Priority</InputLabel>
            <Select
              value={priorityFilter}
              label="Priority"
              onChange={(e) => setPriorityFilter(e.target.value)}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="urgent">Urgent</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Sort By</InputLabel>
            <Select
              value={sortBy}
              label="Sort By"
              onChange={(e) => setSortBy(e.target.value)}
            >
              <MenuItem value="created_at:desc">Newest First</MenuItem>
              <MenuItem value="created_at:asc">Oldest First</MenuItem>
              <MenuItem value="priority:desc">Priority High-Low</MenuItem>
              <MenuItem value="priority:asc">Priority Low-High</MenuItem>
              <MenuItem value="title:asc">Title A-Z</MenuItem>
              <MenuItem value="title:desc">Title Z-A</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {pendingTasks.length === 0 && completedTasks.length === 0 ? (
        <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
          No tasks yet. Add a task using the chat interface!
        </Typography>
      ) : (
        <>
          {pendingTasks.length > 0 && (
            <Box>
              <Typography variant="subtitle1" color="primary" sx={{ mb: 1 }}>
                Pending ({pendingTasks.length})
              </Typography>
              <List dense>
                {pendingTasks.map((task) => (
                  <React.Fragment key={task.id}>
                    <ListItem>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <span>{task.title}</span>
                            <Chip
                              label={task.priority}
                              size="small"
                              sx={{
                                backgroundColor: getPriorityColor(task.priority),
                                color: 'white',
                                fontSize: '0.7rem',
                                height: '20px'
                              }}
                            />
                            {task.recurrence_pattern && (
                              <Chip
                                label={`↻ ${task.recurrence_pattern}`}
                                size="small"
                                sx={{
                                  backgroundColor: '#8b5cf6',
                                  color: 'white',
                                  fontSize: '0.7rem',
                                  height: '20px'
                                }}
                              />
                            )}
                            {task.due_date && (
                              <Chip
                                label={formatDueDate(task.due_date)}
                                size="small"
                                sx={{
                                  backgroundColor: isOverdue(task) ? '#ef4444' : '#3b82f6',
                                  color: 'white',
                                  fontSize: '0.7rem',
                                  height: '20px'
                                }}
                              />
                            )}
                          </Box>
                        }
                        secondary={
                          <>
                            {task.description && (
                              <Typography variant="body2" color="text.secondary">
                                {task.description}
                              </Typography>
                            )}
                            {task.tags && task.tags.length > 0 && (
                              <Box sx={{ mt: 0.5, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                {task.tags.map((tag, idx) => (
                                  <Chip
                                    key={idx}
                                    label={tag}
                                    size="small"
                                    variant="outlined"
                                    sx={{ height: '20px', fontSize: '0.7rem' }}
                                  />
                                ))}
                              </Box>
                            )}
                          </>
                        }
                      />
                      <ListItemSecondaryAction>
                        <IconButton edge="end" onClick={() => handleToggleTask(task)}>
                          <RadioButtonUncheckedIcon color="primary" />
                        </IconButton>
                        <IconButton edge="end" onClick={() => handleDeleteTask(task.id)}>
                          <DeleteIcon color="error" />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </Box>
          )}

          {completedTasks.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle1" color="success.main" sx={{ mb: 1 }}>
                Completed ({completedTasks.length})
              </Typography>
              <List dense>
                {completedTasks.map((task) => (
                  <React.Fragment key={task.id}>
                    <ListItem>
                      <ListItemText
                        primary={
                          <Typography
                            variant="body1"
                            sx={{ textDecoration: 'line-through', color: 'text.disabled' }}
                          >
                            {task.title}
                          </Typography>
                        }
                        secondary={
                          task.description ? (
                            <Typography
                              variant="body2"
                              sx={{ textDecoration: 'line-through', color: 'text.disabled' }}
                            >
                              {task.description}
                            </Typography>
                          ) : null
                        }
                      />
                      <ListItemSecondaryAction>
                        <IconButton edge="end" onClick={() => handleToggleTask(task)}>
                          <CheckCircleIcon color="success" />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </Box>
          )}
        </>
      )}
    </Box>
  );
};

export default TaskList;
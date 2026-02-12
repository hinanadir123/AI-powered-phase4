// React component for displaying tasks

import React, { useState, useEffect } from 'react';
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
  Alert
} from '@mui/material';
import { Task } from '../../types/task';
import apiService from '../../services/api';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import DeleteIcon from '@mui/icons-material/Delete';

interface TaskListProps {
  userId: string;
}

const TaskList: React.FC<TaskListProps> = ({ userId }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTasks();
  }, [userId]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const tasksData = await apiService.getTasks(userId);
      setTasks(tasksData);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch tasks';
      setError(errorMessage);
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTask = async (task: Task) => {
    try {
      if (!task.completed) {
        // Complete the task
        const updatedTask = await apiService.completeTask(userId, task.id);
        setTasks(prevTasks => prevTasks.map(t => t.id === task.id ? updatedTask : t));
      } else {
        // Reopen the task - in a real app you might have an endpoint for this
        console.log('Reopening task:', task.id);
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
      // Remove the task from the UI
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete task';
      setError(errorMessage);
      console.error('Error deleting task:', err);
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

  // Group tasks by status
  const pendingTasks = tasks.filter(task => !task.completed);
  const completedTasks = tasks.filter(task => task.completed);

  return (
    <Box sx={{ width: '100%', height: '100%', overflow: 'auto', p: 1 }}>
      <Typography variant="h6" gutterBottom>
        My Tasks
      </Typography>

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
                        primary={task.title}
                        secondary={
                          task.description ? (
                            <Typography variant="body2" color="text.secondary">
                              {task.description}
                            </Typography>
                          ) : null
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
                        <Chip label="Completed" color="success" size="small" />
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
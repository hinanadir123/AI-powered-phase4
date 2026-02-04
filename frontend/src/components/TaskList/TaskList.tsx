// React component for displaying tasks

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemSecondaryAction, 
  IconButton, 
  Checkbox, 
  Typography, 
  Paper, 
  Chip,
  Divider
} from '@mui/material';
import { Task } from '../../types/task';
import apiService from '../../services/api';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import DeleteIcon from '@mui/icons-material/Delete';

interface TaskListProps {
  userId: string;
  onTaskUpdate?: () => void;
}

const TaskList: React.FC<TaskListProps> = ({ userId, onTaskUpdate }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTasks();
  }, [userId, onTaskUpdate]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const tasksData = await apiService.getTasks(userId);
      setTasks(tasksData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTask = async (task: Task) => {
    try {
      if (task.status === 'pending') {
        // Complete the task
        await apiService.completeTask(userId, task.id);
      } else {
        // For this example, we'll just toggle back to pending if needed
        // In a real app, you might have an undo completion endpoint
        console.log('Reopening task:', task.id);
      }
      // Refresh the task list
      fetchTasks();
      onTaskUpdate?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await apiService.deleteTask(userId, taskId);
      // Refresh the task list
      fetchTasks();
      onTaskUpdate?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography>Loading tasks...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography color="error">Error: {error}</Typography>
      </Box>
    );
  }

  // Group tasks by status
  const pendingTasks = tasks.filter(task => task.status === 'pending');
  const completedTasks = tasks.filter(task => task.status === 'completed');

  return (
    <Box sx={{ width: '100%' }}>
      <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          My Tasks
        </Typography>
        
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
      </Paper>
    </Box>
  );
};

export default TaskList;
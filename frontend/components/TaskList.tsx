'use client';

import React, { useState, useEffect } from 'react';
import { taskApi } from '../lib/api';
import { Task as TaskType } from '../types/task';
import EmptyState from './EmptyState';

type TaskListProps = {
  userId: string;
};

const TaskList = ({ userId }: TaskListProps) => {
  const [tasks, setTasks] = useState<TaskType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    const loadTasks = async () => {
      try {
        setLoading(true);
        const data = await taskApi.getTasks(userId);
        setTasks(data);
      } catch (err) {
        setError('Failed to load tasks');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadTasks();
  }, [userId, refreshTrigger]);

  const handleDeleteTask = async (taskId: number) => {
    try {
      await taskApi.deleteTask(userId, taskId);
      // Refresh the task list after deletion
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      setError('Failed to delete task');
      console.error(err);
    }
  };

  const handleToggleTaskCompletion = async (taskId: number) => {
    try {
      const updatedTask = await taskApi.toggleTaskCompletion(userId, taskId);
      // Update the task in the local state
      setTasks(prevTasks =>
        prevTasks.map(task =>
          task.id === taskId ? updatedTask : task
        )
      );
    } catch (err) {
      setError('Failed to update task');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4 rounded">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (tasks.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-800">Your Tasks</h2>
        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
          {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
        </span>
      </div>

      <ul className="space-y-3">
        {tasks.map((task) => (
          <li
            key={task.id}
            className={`p-4 rounded-xl border transition-all duration-200 hover:shadow-md ${
              task.completed
                ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200 text-green-800'
                : 'bg-white border-gray-200 shadow-sm'
            }`}
          >
            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => handleToggleTaskCompletion(task.id)}
                className="mt-1 h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div className="flex-1 min-w-0">
                <h3 className={`font-medium truncate ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                  {task.title}
                </h3>
                {task.description && (
                  <p className={`text-sm mt-1 truncate ${task.completed ? 'text-gray-400' : 'text-gray-500'}`}>
                    {task.description}
                  </p>
                )}
                <div className="flex items-center text-xs text-gray-400 mt-2">
                  <span>Created: {new Date(task.created_at).toLocaleDateString()}</span>
                  {task.completed && (
                    <span className="ml-2">Completed: {new Date(task.updated_at).toLocaleDateString()}</span>
                  )}
                </div>
              </div>
              <button
                onClick={() => handleDeleteTask(task.id)}
                className="ml-2 text-red-500 hover:text-red-700 transition-colors duration-200"
                aria-label="Delete task"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TaskList;
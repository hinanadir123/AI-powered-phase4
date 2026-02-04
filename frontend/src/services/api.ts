// API service for the Todo AI Chatbot frontend

import axios, { AxiosInstance } from 'axios';
import { ChatRequest, ChatResponse, Task, User } from '../types/task';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

class ApiService {
  private apiClient: AxiosInstance;

  constructor() {
    this.apiClient = axios.create({
      baseURL: BACKEND_URL,
      timeout: 10000, // 10 seconds timeout
    });

    // Add request interceptor to include auth token
    this.apiClient.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor to handle token expiration
    this.apiClient.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        if (error.response?.status === 401) {
          // Token might be expired, redirect to login
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Chat API methods
  async sendMessage(userId: string, request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await this.apiClient.post<ChatResponse>(`/api/${userId}/chat`, request);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Task API methods
  async getTasks(userId: string): Promise<Task[]> {
    try {
      const response = await this.apiClient.get<{ tasks: Task[] }>(`/api/${userId}/tasks`);
      return response.data.tasks;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createTask(userId: string, taskData: Partial<Task>): Promise<Task> {
    try {
      const response = await this.apiClient.post<Task>(`/api/${userId}/tasks`, taskData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateTask(userId: string, taskId: string, taskData: Partial<Task>): Promise<Task> {
    try {
      const response = await this.apiClient.put<Task>(`/api/${userId}/tasks/${taskId}`, taskData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteTask(userId: string, taskId: string): Promise<boolean> {
    try {
      await this.apiClient.delete(`/api/${userId}/tasks/${taskId}`);
      return true;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async completeTask(userId: string, taskId: string): Promise<Task> {
    try {
      const response = await this.apiClient.post<Task>(`/api/${userId}/tasks/${taskId}/complete`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // User API methods
  async getCurrentUser(): Promise<User> {
    try {
      const response = await this.apiClient.get<User>('/auth/me');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Helper method to handle errors
  private handleError(error: any): Error {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // Server responded with error status
        const { data, status } = error.response;
        return new Error(`API Error: ${status} - ${data.message || data.detail || 'Unknown error'}`);
      } else if (error.request) {
        // Request made but no response received
        return new Error('Network Error: No response received from server');
      } else {
        // Something else happened
        return new Error(`Request Error: ${error.message}`);
      }
    }
    return new Error('Unknown error occurred');
  }
}

export default new ApiService();
// API service for the Todo AI Chatbot frontend

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { Task } from '../types/task';
import authService from './auth';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

class ApiService {
  private apiClient: AxiosInstance;

  constructor() {
    this.apiClient = axios.create({
      baseURL: `${BACKEND_URL}/api`,
      timeout: 15000, // 15 seconds timeout
    });

    // Add request interceptor to include auth token
    this.apiClient.interceptors.request.use(
      (config) => {
        const token = authService.getToken();
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
          authService.logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Chat API methods
  async sendMessage(userId: string, request: any): Promise<any> {
    try {
      const response: AxiosResponse = await this.apiClient.post(`/${userId}/chat`, request);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Task API methods
  async getTasks(
    userId: string,
    params?: {
      status?: string;
      priority?: string;
      tags?: string;
      search?: string;
      due_from?: string;
      due_to?: string;
      sort?: string;
    }
  ): Promise<Task[]> {
    try {
      const queryParams = new URLSearchParams();
      if (params?.status) queryParams.append('status_param', params.status);
      if (params?.priority) queryParams.append('priority', params.priority);
      if (params?.tags) queryParams.append('tags', params.tags);
      if (params?.search) queryParams.append('search', params.search);
      if (params?.due_from) queryParams.append('due_from', params.due_from);
      if (params?.due_to) queryParams.append('due_to', params.due_to);
      if (params?.sort) queryParams.append('sort', params.sort);

      const url = `/${userId}/tasks${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
      const response: AxiosResponse<Task[]> = await this.apiClient.get(url);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getTags(userId: string): Promise<Array<{ id: number; name: string }>> {
    try {
      const response = await this.apiClient.get(`/${userId}/tags`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createTask(userId: string, taskData: Partial<Task>): Promise<Task> {
    try {
      const response: AxiosResponse<Task> = await this.apiClient.post(`/${userId}/tasks`, taskData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateTask(userId: string, taskId: number, taskData: Partial<Task>): Promise<Task> {
    try {
      const response: AxiosResponse<Task> = await this.apiClient.put(`/${userId}/tasks/${taskId}`, taskData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteTask(userId: string, taskId: number): Promise<boolean> {
    try {
      await this.apiClient.delete(`/${userId}/tasks/${taskId}`);
      return true;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async completeTask(userId: string, taskId: number): Promise<Task> {
    try {
      const response: AxiosResponse<Task> = await this.apiClient.post(`/${userId}/tasks/${taskId}/complete`);
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
        const message = data?.message || data?.detail || data?.error || 'Unknown error';
        return new Error(`API Error: ${status} - ${message}`);
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
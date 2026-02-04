// Auth service for the Todo AI Chatbot frontend

import axios from 'axios';
import { User } from '../types/task';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

class AuthService {
  private tokenKey = 'access_token';

  // Login method
  async login(email: string, password: string): Promise<{ user: User; accessToken: string }> {
    try {
      const response = await axios.post(`${BACKEND_URL}/auth/login`, {
        email,
        password
      });

      const { access_token } = response.data;
      this.setToken(access_token);

      // Get user details
      const user = await this.getCurrentUser();

      return { user, accessToken: access_token };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.detail || 'Login failed';
        throw new Error(errorMessage);
      }
      throw new Error('An unexpected error occurred during login');
    }
  }

  // Register method
  async register(email: string, password: string, name: string): Promise<{ user: User; accessToken: string }> {
    try {
      const response = await axios.post(`${BACKEND_URL}/auth/register`, {
        email,
        password,
        name
      });

      const { access_token } = response.data;
      this.setToken(access_token);

      // Get user details
      const user = await this.getCurrentUser();

      return { user, accessToken: access_token };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.detail || 'Registration failed';
        throw new Error(errorMessage);
      }
      throw new Error('An unexpected error occurred during registration');
    }
  }

  // Logout method
  logout(): void {
    localStorage.removeItem(this.tokenKey);
    // Optionally redirect to login page
    window.location.href = '/login';
  }

  // Get current user
  async getCurrentUser(): Promise<User> {
    const token = this.getToken();
    if (!token) {
      throw new Error('No authentication token found');
    }

    try {
      const response = await axios.get(`${BACKEND_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        // If unauthorized, remove token and redirect
        if (error.response?.status === 401) {
          this.logout();
          throw new Error('Session expired. Please log in again.');
        }
        const errorMessage = error.response?.data?.detail || 'Failed to get user details';
        throw new Error(errorMessage);
      }
      throw new Error('An unexpected error occurred while fetching user details');
    }
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = this.getToken();
    return !!token;
  }

  // Get token from localStorage
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  // Set token in localStorage
  setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  // Refresh token (if needed)
  async refreshToken(): Promise<string> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post(`${BACKEND_URL}/auth/refresh`, {
        refresh_token: refreshToken
      });

      const { access_token } = response.data;
      this.setToken(access_token);
      return access_token;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.detail || 'Token refresh failed';
        throw new Error(errorMessage);
      }
      throw new Error('An unexpected error occurred during token refresh');
    }
  }
}

export default new AuthService();
// Authentication service for the Todo AI Chatbot frontend

import axios from 'axios';

interface User {
  id: string;
  email: string;
  name: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

class AuthService {
  private baseUrl: string;
  private tokenKey = 'access_token';

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  }

  async login(email: string, password: string): Promise<LoginResponse> {
    try {
      const response = await axios.post<LoginResponse>(`${this.baseUrl}/auth/login`, {
        email,
        password
      });

      // Store the token in localStorage
      localStorage.setItem(this.tokenKey, response.data.access_token);
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || 'Login failed';
        throw new Error(message);
      }
      throw new Error('An unexpected error occurred during login');
    }
  }

  async register(email: string, password: string, name: string): Promise<LoginResponse> {
    try {
      const response = await axios.post<LoginResponse>(`${this.baseUrl}/auth/register`, {
        email,
        password,
        name
      });

      // Store the token in localStorage
      localStorage.setItem(this.tokenKey, response.data.access_token);
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || 'Registration failed';
        throw new Error(message);
      }
      throw new Error('An unexpected error occurred during registration');
    }
  }

  async logout(): Promise<void> {
    // Remove the token from localStorage
    localStorage.removeItem(this.tokenKey);
  }

  isAuthenticated(): boolean {
    const token = localStorage.getItem(this.tokenKey);
    return !!token;
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  removeToken(): void {
    localStorage.removeItem(this.tokenKey);
  }
}

export default new AuthService();
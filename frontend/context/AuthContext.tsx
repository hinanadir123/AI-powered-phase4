'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

type AuthContextType = {
  user: { email: string; name?: string } | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  register: (name: string, email: string, password: string) => Promise<boolean>;
  loading: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Get the backend API URL from environment variable
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<{ email: string; name?: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on initial load
    const checkLoginStatus = async () => {
      const authToken = localStorage.getItem('authToken');
      const userEmail = localStorage.getItem('userEmail');
      const userName = localStorage.getItem('userName');

      if (authToken && userEmail) {
        try {
          // Verify the token is still valid by making a request to the backend
          const response = await fetch(`${API_BASE_URL}/health`, {
            headers: {
              'Authorization': `Bearer ${authToken}`
            }
          });

          if (response.ok) {
            setUser({
              email: userEmail,
              name: userName || undefined
            });
          } else {
            // If token is invalid, clear stored data
            localStorage.removeItem('authToken');
            localStorage.removeItem('userEmail');
            localStorage.removeItem('userName');
          }
        } catch (error) {
          console.error('Token verification failed:', error);
          // Clear stored data if there's an error
          localStorage.removeItem('authToken');
          localStorage.removeItem('userEmail');
          localStorage.removeItem('userName');
        }
      }
      setLoading(false);
    };

    checkLoginStatus();
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    setLoading(true);

    try {
      // Make a request to the backend login endpoint
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        // Store the JWT token received from the backend
        localStorage.setItem('authToken', data.access_token);
        localStorage.setItem('userEmail', email);

        setUser({ email });
        return true;
      } else {
        const errorData = await response.json();
        console.error('Login failed:', errorData.detail || 'Unknown error');
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string): Promise<boolean> => {
    setLoading(true);

    try {
      // Make a request to the backend register endpoint
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        // After successful registration, log the user in
        const loginResult = await login(email, password);
        return loginResult;
      } else {
        const errorData = await response.json();
        console.error('Registration failed:', errorData.detail || 'Unknown error');
        return false;
      }
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    // Clear user data from localStorage
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('userName');

    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    register,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
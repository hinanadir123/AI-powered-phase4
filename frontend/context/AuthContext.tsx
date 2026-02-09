'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: () => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Check for existing session on initial load
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // In a real app, you would validate the token with the backend
      // For now, we'll create a mock user based on stored data
      const userData = localStorage.getItem('user_data');
      if (userData) {
        try {
          const parsedUser = JSON.parse(userData);
          setUser(parsedUser);
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      // In a real app, you would make an API call to your backend
      // For this demo, we'll simulate a successful login
      const mockUser = {
        id: `user_${Date.now()}`,
        email,
        name: email.split('@')[0] // Use email prefix as name
      };

      // Store user data and token
      localStorage.setItem('user_data', JSON.stringify(mockUser));
      localStorage.setItem('access_token', `mock_token_${Date.now()}`);
      
      setUser(mockUser);
      router.push('/dashboard');
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (email: string, password: string, name: string) => {
    try {
      // In a real app, you would make an API call to register the user
      // For this demo, we'll simulate a successful registration
      const mockUser = {
        id: `user_${Date.now()}`,
        email,
        name
      };

      // Store user data and token
      localStorage.setItem('user_data', JSON.stringify(mockUser));
      localStorage.setItem('access_token', `mock_token_${Date.now()}`);
      
      setUser(mockUser);
      router.push('/dashboard');
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const logout = () => {
    // Clear user data and token
    localStorage.removeItem('user_data');
    localStorage.removeItem('access_token');
    
    setUser(null);
    router.push('/landing');
  };

  const isAuthenticated = () => {
    return !!user;
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated
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
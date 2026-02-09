// Type definitions for the Todo AI Chatbot frontend

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'completed';
  created_at: string;
  completed_at?: string;
  user_id: string;
  conversation_id?: string;
}

export interface Message {
  id: string;
  content: string;
  sender_type: 'user' | 'ai';
  timestamp: string;
  conversation_id: string;
  user_id: string;
}

export interface Conversation {
  id: string;
  title?: string;
  created_at: string;
  updated_at: string;
  user_id: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  tasks_updated: Task[];
  next_message_expected: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}
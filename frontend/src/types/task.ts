// Types for the Todo AI Chatbot frontend

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'completed';
  created_at: string; // ISO date string
  completed_at?: string; // ISO date string
  user_id: string;
  conversation_id?: string;
}

export interface Conversation {
  id: string;
  title?: string;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  user_id: string;
}

export interface Message {
  id: string;
  content: string;
  sender_type: 'user' | 'ai';
  timestamp: string; // ISO date string
  conversation_id: string;
  user_id: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  auth_provider: string;
  auth_provider_user_id: string;
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

export interface ErrorResponse {
  error: string;
  detail: string;
  code: string;
}
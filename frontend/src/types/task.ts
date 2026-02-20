// Type definitions for the Todo AI Chatbot frontend

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export type PriorityLevel = 'low' | 'medium' | 'high' | 'urgent';

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  // Phase 5 fields
  priority: PriorityLevel;
  tags: string[];
  due_date?: string;
  reminder_time?: string;
  recurrence_pattern?: string;
  recurrence_end_date?: string;
  parent_task_id?: number;
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
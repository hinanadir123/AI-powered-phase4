// frontend/types/task.ts

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}
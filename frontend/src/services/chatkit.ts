// Chat service for connecting frontend to the chat API

import apiService from './api';
import { ChatRequest, ChatResponse } from '../types/task';

class ChatService {
  // This service would typically handle chat-specific functionality
  // For now, we'll just use the existing apiService for chat operations
  
  async sendMessage(userId: string, message: string, conversationId?: string): Promise<ChatResponse> {
    const request: ChatRequest = {
      message,
      conversation_id: conversationId
    };
    
    return await apiService.sendMessage(userId, request);
  }
}

export default new ChatService();
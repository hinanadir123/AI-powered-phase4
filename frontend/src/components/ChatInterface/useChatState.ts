import { useState, useEffect } from 'react';
import { Message } from '../../types/task';

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  conversationId: string | null;
}

interface UseChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  addMessage: (message: Message) => void;
  setIsLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  setConversationId: (id: string | null) => void;
  clearMessages: () => void;
}

export const useChatState = (): UseChatState => {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    error: null,
    conversationId: null,
  });

  const addMessage = (message: Message) => {
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, message]
    }));
  };

  const setIsLoading = (isLoading: boolean) => {
    setState(prev => ({
      ...prev,
      isLoading
    }));
  };

  const setError = (error: string | null) => {
    setState(prev => ({
      ...prev,
      error
    }));
  };

  const setConversationId = (id: string | null) => {
    setState(prev => ({
      ...prev,
      conversationId: id
    }));
  };

  const clearMessages = () => {
    setState(prev => ({
      ...prev,
      messages: []
    }));
  };

  return {
    messages: state.messages,
    isLoading: state.isLoading,
    error: state.error,
    addMessage,
    setIsLoading,
    setError,
    setConversationId,
    clearMessages
  };
};
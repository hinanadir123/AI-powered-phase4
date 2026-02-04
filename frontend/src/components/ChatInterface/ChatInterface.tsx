// React component for the chat interface

import React, { useState, useEffect, useRef } from 'react';
import { Box, TextField, Button, Typography, Paper, List, ListItem, ListItemText, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { ChatRequest, ChatResponse, Message } from '../../types/task';
import apiService from '../../services/api';
import authService from '../../services/auth';

interface ChatInterfaceProps {
  userId: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ userId }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    try {
      setIsLoading(true);

      // Add user message to UI immediately
      const userMessage: Message = {
        id: Date.now().toString(),
        content: inputMessage,
        sender_type: 'user',
        timestamp: new Date().toISOString(),
        conversation_id: conversationId || '',
        user_id: userId
      };

      setMessages(prev => [...prev, userMessage]);
      const messageToSend = inputMessage;
      setInputMessage('');

      // Send message to backend
      const request: ChatRequest = {
        message: messageToSend,
        conversation_id: conversationId || undefined
      };

      const response: ChatResponse = await apiService.sendMessage(userId, request);

      // Update conversation ID if new conversation was created
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add AI response to messages
      const aiMessage: Message = {
        id: `ai-${Date.now()}`,
        content: response.response,
        sender_type: 'ai',
        timestamp: new Date().toISOString(),
        conversation_id: response.conversation_id,
        user_id: userId
      };

      setMessages(prev => [...prev, aiMessage]);

      // Handle any updated tasks
      if (response.tasks_updated.length > 0) {
        // Optionally update task list in parent component
        console.log('Updated tasks:', response.tasks_updated);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        sender_type: 'ai',
        timestamp: new Date().toISOString(),
        conversation_id: conversationId || '',
        user_id: userId
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper elevation={3} sx={{ flex: 1, display: 'flex', flexDirection: 'column', mb: 2, overflow: 'hidden' }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', backgroundColor: '#f5f5f5' }}>
          <Typography variant="h6">AI Task Assistant</Typography>
        </Box>
        
        <List sx={{ flex: 1, overflowY: 'auto', p: 2 }}>
          {messages.map((msg, index) => (
            <ListItem
              key={msg.id}
              alignItems="flex-start"
              sx={{
                justifyContent: msg.sender_type === 'user' ? 'flex-end' : 'flex-start',
                mb: 1
              }}
            >
              <Paper
                sx={{
                  maxWidth: '70%',
                  p: 1.5,
                  borderRadius: msg.sender_type === 'user' ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
                  backgroundColor: msg.sender_type === 'user' ? '#e3f2fd' : '#f5f5f5',
                  alignSelf: msg.sender_type === 'user' ? 'flex-end' : 'flex-start'
                }}
              >
                <ListItemText
                  primary={msg.content}
                  secondary={
                    <Typography
                      sx={{ display: 'inline' }}
                      component="span"
                      variant="caption"
                      color="text.primary"
                    >
                      {msg.sender_type === 'user' ? 'You' : 'Assistant'} • {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </Typography>
                  }
                />
              </Paper>
            </ListItem>
          ))}
          {isLoading && (
            <ListItem alignItems="flex-start" sx={{ justifyContent: 'flex-start', mb: 1 }}>
              <Paper
                sx={{
                  maxWidth: '70%',
                  p: 1.5,
                  borderRadius: '20px 20px 20px 4px',
                  backgroundColor: '#f5f5f5',
                  alignSelf: 'flex-start'
                }}
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      Thinking...
                    </Box>
                  }
                />
              </Paper>
            </ListItem>
          )}
          <div ref={messagesEndRef} />
        </List>
        
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              rows={2}
              variant="outlined"
              placeholder="Ask me to add, list, complete, or manage your tasks..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleSendMessage}
              disabled={isLoading || !inputMessage.trim()}
              endIcon={<SendIcon />}
              sx={{ height: 'fit-content' }}
            >
              Send
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatInterface;
// React component for the chat interface

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import apiService from '../../services/api';

interface Message {
  id: string;
  content: string;
  sender_type: 'user' | 'ai';
  timestamp: string;
  conversation_id: string;
  user_id: string;
}

interface ChatResponse {
  response: string;
  conversation_id: string;
  tasks_updated: any[];
  next_message_expected: boolean;
}

interface ChatRequest {
  message: string;
  conversation_id?: string;
}

interface ChatInterfaceProps {
  userId: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ userId }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
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
      setError(null);

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
      if (response.tasks_updated && response.tasks_updated.length > 0) {
        // Optionally update task list in parent component
        console.log('Updated tasks:', response.tasks_updated);
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      setError(error.message || 'An error occurred while sending the message');
      
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content: error.message || 'Sorry, I encountered an error processing your request. Please try again.',
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
      <Paper
        elevation={3}
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          borderRadius: 2
        }}
      >
        <Box sx={{
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px 8px 0 0'
        }}>
          <Typography variant="h6">AI Task Assistant</Typography>
        </Box>

        <List
          sx={{
            flex: 1,
            overflowY: 'auto',
            p: 2,
            bgcolor: '#fafafa'
          }}
        >
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {messages.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
              <Typography variant="h6" gutterBottom>
                Welcome to your AI Task Assistant!
              </Typography>
              <Typography variant="body2">
                You can manage your tasks using natural language. Try commands like:
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                "Add a task to buy groceries"
              </Typography>
              <Typography variant="body2">
                "Show me my tasks"
              </Typography>
              <Typography variant="body2">
                "Mark the grocery task as complete"
              </Typography>
            </Box>
          ) : (
            <>
              {messages.map((msg) => (
                <React.Fragment key={msg.id}>
                  <ListItem
                    alignItems="flex-start"
                    sx={{
                      justifyContent: msg.sender_type === 'user' ? 'flex-end' : 'flex-start',
                      py: 1
                    }}
                  >
                    <Paper
                      sx={{
                        maxWidth: '75%',
                        p: 1.5,
                        borderRadius: msg.sender_type === 'user'
                          ? '18px 18px 4px 18px'
                          : '18px 18px 18px 4px',
                        backgroundColor: msg.sender_type === 'user'
                          ? '#e3f2fd'
                          : '#ffffff',
                        boxShadow: 1
                      }}
                    >
                      <ListItemText
                        primary={msg.content}
                        secondary={
                          <Typography
                            sx={{ display: 'inline' }}
                            component="span"
                            variant="caption"
                            color="text.secondary"
                          >
                            {msg.sender_type === 'user' ? 'You' : 'Assistant'} •{' '}
                            {new Date(msg.timestamp).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </Typography>
                        }
                      />
                    </Paper>
                  </ListItem>
                </React.Fragment>
              ))}
              {isLoading && (
                <ListItem
                  alignItems="flex-start"
                  sx={{
                    justifyContent: 'flex-start',
                    py: 1
                  }}
                >
                  <Paper
                    sx={{
                      maxWidth: '75%',
                      p: 1.5,
                      borderRadius: '18px 18px 18px 4px',
                      backgroundColor: '#ffffff',
                      boxShadow: 1
                    }}
                  >
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <CircularProgress size={16} sx={{ mr: 1 }} />
                          <Typography variant="body2">Thinking...</Typography>
                        </Box>
                      }
                    />
                  </Paper>
                </ListItem>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </List>

        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              rows={2}
              variant="outlined"
              placeholder="Ask me to add, list, complete, or manage your tasks..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isLoading}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                }
              }}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleSendMessage}
              disabled={isLoading || !inputMessage.trim()}
              endIcon={<SendIcon />}
              sx={{
                height: 'fit-content',
                alignSelf: 'flex-end',
                borderRadius: 2,
                px: 3
              }}
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
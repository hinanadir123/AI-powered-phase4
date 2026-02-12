"use client";

import dynamic from 'next/dynamic';
import { useParams } from 'next/navigation';
import { Box, Container, Typography } from '@mui/material';
import { useEffect, useState } from 'react';

// Dynamically import the ChatInterface component to avoid SSR issues
const ChatInterface = dynamic(() => import('../../src/components/ChatInterface/ChatInterface'), {
  ssr: false,
  loading: () => <div>Loading chat interface...</div>
});

export default function ChatPage() {
  const params = useParams();
  const [userId, setUserId] = useState<string | null>(null);

  // In a real app, you would get the user ID from authentication context
  useEffect(() => {
    // For now, we'll use a mock user ID or get from localStorage
    const mockUserId = localStorage.getItem('mock_user_id') || 'user-123';
    setUserId(mockUserId);
  }, []);

  if (!userId) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Typography variant="h5" align="center">
          Loading chat interface...
        </Typography>
      </Container>
    );
  }

  return (
    <Box sx={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#f5f5f5'
    }}>
      <Box sx={{
        px: 2,
        py: 1,
        backgroundColor: '#1976d2',
        color: 'white',
        display: 'flex',
        alignItems: 'center'
      }}>
        <Typography variant="h6">
          AI Task Assistant
        </Typography>
      </Box>
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        <ChatInterface userId={userId} />
      </Box>
    </Box>
  );
}

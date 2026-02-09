"use client";

import { useState, useEffect } from 'react';
import { Box, Container, Typography, Grid } from '@mui/material';
import dynamic from 'next/dynamic';

// Dynamically import components to avoid SSR issues
const ChatInterface = dynamic(() => import('../../src/components/ChatInterface/ChatInterface'), {
  ssr: false,
  loading: () => <div>Loading chat interface...</div>
});

const TaskList = dynamic(() => import('../../src/components/TaskList/TaskList'), {
  ssr: false,
  loading: () => <div>Loading task list...</div>
});

export default function DashboardPage() {
  const [userId, setUserId] = useState<string | null>(null);

  // Initialize with mock authentication token for testing
  useEffect(() => {
    // Set a mock token for testing if none exists
    if (!localStorage.getItem('access_token')) {
      localStorage.setItem('access_token', 'mock-token-for-testing');
    }
    
    // Set a mock user ID for testing
    const mockUserId = localStorage.getItem('mock_user_id') || 'user-123';
    localStorage.setItem('mock_user_id', mockUserId);
    setUserId(mockUserId);
  }, []);

  if (!userId) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h5" align="center">
          Loading dashboard...
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        AI Task Management Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Box sx={{
            backgroundColor: 'white',
            borderRadius: 2,
            boxShadow: 3,
            height: '60vh',
            overflow: 'hidden'
          }}>
            <Typography variant="h6" sx={{ p: 2, backgroundColor: '#f5f5f5', borderRadius: '8px 8px 0 0' }}>
              AI Task Assistant
            </Typography>
            <Box sx={{ height: 'calc(100% - 60px)', overflow: 'hidden' }}>
              <ChatInterface userId={userId} />
            </Box>
          </Box>
        </Grid>

        <Grid item xs={12} md={6}>
          <Box sx={{
            backgroundColor: 'white',
            borderRadius: 2,
            boxShadow: 3,
            height: '60vh',
            overflow: 'hidden'
          }}>
            <Typography variant="h6" sx={{ p: 2, backgroundColor: '#f5f5f5', borderRadius: '8px 8px 0 0' }}>
              Your Tasks
            </Typography>
            <Box sx={{ height: 'calc(100% - 60px)', overflow: 'auto', p: 1 }}>
              <TaskList userId={userId} />
            </Box>
          </Box>
        </Grid>
      </Grid>
    </Container>
  );
}
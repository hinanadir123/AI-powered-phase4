'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useRouter } from 'next/navigation';
import TaskList from '../../components/TaskList';
import TaskFormModal from '../../components/TaskFormModal';
import AddTaskButton from '../../components/AddTaskButton';
import Link from 'next/link';

export default function DashboardPage() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    // If user is not authenticated and not loading, redirect to landing page
    if (!loading && !user) {
      router.push('/landing');
    }
  }, [user, loading, router]);

  const handleAddTask = () => {
    // Ensure user is logged in before allowing to add tasks
    if (!user) {
      router.push('/landing');
      return;
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleTaskCreated = () => {
    // Trigger a refresh of the task list
    setRefreshTrigger(prev => prev + 1);
  };

  // Show loading state while checking auth status
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-gray-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-300">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  // If not authenticated, redirect to landing page (though useEffect should handle this)
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-gray-950">
        <div className="text-center">
          <p className="text-xl text-gray-300 mb-4">You need to be logged in to access the dashboard.</p>
          <Link href="/landing" className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition duration-300">
            Go to Homepage
          </Link>
        </div>
      </div>
    );
  }

  // Use email as a unique identifier for the user in this demo
  const userId = user.email;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-950">
      <header className="bg-gray-800/50 backdrop-blur-md border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-5 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl md:text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-300">
            TaskFlow Dashboard
          </h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-300 hidden sm:block">
              Welcome, {user.name || user.email.split('@')[0]}
            </span>
            <button
              onClick={logout}
              className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white font-medium py-2 px-4 rounded-lg transition duration-300"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="bg-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-2xl p-6 shadow-xl shadow-blue-500/5">
          <TaskList userId={userId} key={refreshTrigger} />
        </div>

        {/* Add task button */}
        <AddTaskButton onClick={handleAddTask} />

        {/* Task form modal */}
        <TaskFormModal
          userId={userId}
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          onTaskCreated={handleTaskCreated}
        />
      </main>
    </div>
  );
}
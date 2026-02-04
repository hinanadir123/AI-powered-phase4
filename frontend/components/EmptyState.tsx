import React from 'react';

const EmptyState = () => {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-dashed border-blue-200 rounded-2xl w-24 h-24 flex items-center justify-center mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>
      <h3 className="text-2xl font-bold text-gray-900 mb-2">No tasks yet</h3>
      <p className="text-gray-600 mb-6 text-center max-w-md">
        Get started by creating your first task. Click the button below to add a new task to your list.
      </p>
      <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium">
        Click the + button to add your first task
      </div>
    </div>
  );
};

export default EmptyState;
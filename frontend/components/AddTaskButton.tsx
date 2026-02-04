import React from 'react';

type AddTaskButtonProps = {
  onClick: () => void;
};

const AddTaskButton = ({ onClick }: AddTaskButtonProps) => {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-8 right-8 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold py-4 px-6 rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 z-10"
      aria-label="Add new task"
    >
      <div className="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        <span>Add Task</span>
      </div>
    </button>
  );
};

export default AddTaskButton;
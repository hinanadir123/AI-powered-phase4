'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import Link from 'next/link';

export default function LandingPage() {
  const { user, loading } = useAuth();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-950 text-white overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 left-1/4 w-[800px] h-[800px] bg-blue-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-indigo-500/10 rounded-full blur-3xl animate-pulse-slow-delayed"></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
              <span className="font-bold text-lg">TF</span>
            </div>
            <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-300">
              TaskFlow
            </span>
          </div>
          
          <div className="flex items-center space-x-4">
            {user ? (
              <Link 
                href="/dashboard" 
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 text-sm font-medium shadow-lg shadow-blue-500/20"
              >
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link 
                  href="/login" 
                  className="text-gray-300 hover:text-white transition-colors duration-300 text-sm font-medium"
                >
                  Login
                </Link>
                <Link 
                  href="/signup" 
                  className="px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 text-sm font-medium shadow-lg shadow-blue-500/20"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-20">
        <div className="flex flex-col items-center text-center">
          <div className={`transition-all duration-700 ease-out ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <h1 className="text-5xl md:text-7xl font-bold max-w-3xl leading-tight">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-300 to-blue-400">
                A Todo Experience
              </span>{' '}
              <br />
              <span className="text-white">Like You've Never Seen.</span>
            </h1>
            
            <p className="mt-6 text-xl text-gray-300 max-w-2xl">
              Streamline your workflow with our intuitive task management platform. 
              Focus on what matters most with our distraction-free interface.
            </p>
            
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                href={user ? "/dashboard" : "/signup"}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 text-base font-medium shadow-lg shadow-blue-500/30 hover:shadow-blue-500/40"
              >
                {user ? "Go to Dashboard" : "Get Started"}
              </Link>
              
              <Link 
                href="/demo"
                className="px-8 py-4 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl hover:bg-gray-700/50 transition-all duration-300 text-base font-medium"
              >
                Explore Dashboard
              </Link>
            </div>
          </div>
          
          {/* Premium UI Preview */}
          <div className={`mt-20 transition-all duration-1000 ease-out delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            <div className="relative bg-gray-800/30 backdrop-blur-xl border border-gray-700/50 rounded-2xl p-6 max-w-4xl w-full shadow-2xl shadow-blue-500/10">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-indigo-500/5 rounded-2xl"></div>
              <div className="relative z-10">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold">Your Tasks</h2>
                  <div className="flex space-x-2">
                    <button className="px-3 py-1 bg-gray-700/50 rounded-lg text-sm hover:bg-gray-600/50 transition">All</button>
                    <button className="px-3 py-1 bg-gray-700/50 rounded-lg text-sm hover:bg-gray-600/50 transition">Pending</button>
                    <button className="px-3 py-1 bg-gray-700/50 rounded-lg text-sm hover:bg-gray-600/50 transition">Completed</button>
                  </div>
                </div>
                
                <div className="space-y-4">
                  {[1, 2, 3].map((item) => (
                    <div 
                      key={item}
                      className="p-4 bg-gray-900/50 backdrop-blur-sm border border-gray-700/30 rounded-xl hover:border-gray-600/50 transition-all duration-300"
                    >
                      <div className="flex items-start space-x-3">
                        <input 
                          type="checkbox" 
                          className="mt-1 h-5 w-5 rounded border-gray-600 bg-gray-800 text-blue-500 focus:ring-blue-500 focus:ring-offset-gray-900"
                        />
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium truncate">Sample task {item}</h3>
                          <p className="text-sm text-gray-400 mt-1 truncate">This is a sample task description</p>
                          <div className="text-xs text-gray-500 mt-2">Created: Today</div>
                        </div>
                        <button className="text-gray-400 hover:text-red-400 transition-colors">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="mt-6 flex justify-center">
                  <button className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg shadow-blue-500/30 hover:shadow-blue-500/40">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Animation styles */}
      <style jsx global>{`
        @keyframes pulse-slow {
          0%, 100% { opacity: 0.1; }
          50% { opacity: 0.15; }
        }
        
        .animate-pulse-slow {
          animation: pulse-slow 8s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        .animate-pulse-slow-delayed {
          animation: pulse-slow 8s cubic-bezier(0.4, 0, 0.6, 1) infinite;
          animation-delay: 2s;
        }
      `}</style>
    </div>
  );
}
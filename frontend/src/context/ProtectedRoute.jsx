import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
import React from 'react';

export const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAuth();
  const location = useLocation();
  
  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="flex flex-col items-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
          <p className="mt-4 text-sm font-medium text-gray-500">Authenticating...</p>
        </div>
      </div>
    );
  }

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

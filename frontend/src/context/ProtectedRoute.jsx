import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

export const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  
  // For now, always allow access since backend auth isn't integrated yet.
  // TODO: Swap this to check for `!token` or `!user` and redirect to /login
  const isAuthenticated = true; 

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

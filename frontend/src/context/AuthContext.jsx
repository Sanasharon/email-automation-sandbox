import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  // Store token in memory, not localStorage, to mitigate XSS risks.
  // In a real app, this might be initialized by an httpOnly cookie check endpoint.
  const [token, setToken] = useState(null);
  
  // Mock role-based data. In a real app, this comes from the decoded token or /me endpoint.
  const [user, setUser] = useState({
    id: 'usr_1',
    name: 'Admin User',
    role: 'admin', // or 'viewer'
  });

  // Basic capability checking
  const canEdit = user?.role === 'admin';

  return (
    <AuthContext.Provider value={{ token, setToken, user, canEdit }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

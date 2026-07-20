import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

  useEffect(() => {
    const fetchUser = async () => {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const response = await axios.get(`${baseURL}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (response.data?.success) {
          setUser(response.data.user);
        } else {
          logout();
        }
      } catch (error) {
        console.error('Auth verification failed', error);
        logout();
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, [token, baseURL]);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${baseURL}/auth/login`, { email, password });
      if (response.data?.token) {
        const newToken = response.data.token;
        localStorage.setItem('token', newToken);
        setToken(newToken);
        return { success: true };
      }
      return { success: false, error: 'Invalid response from server' };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed. Please check your credentials.' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const canEdit = user?.role === 'Admin'; // Based on our db role

  return (
    <AuthContext.Provider value={{ token, setToken, user, loading, login, logout, canEdit }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api, axiosClient } from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [verifying, setVerifying] = useState(true);
  const [authError, setAuthError] = useState(null);

  const verifyAuth = useCallback(async () => {
    const currentToken = localStorage.getItem('token');
    if (!currentToken) {
      setVerifying(false);
      setUser(null);
      setToken(null);
      return;
    }

    try {
      setVerifying(true);
      axiosClient.defaults.headers.Authorization = `Bearer ${currentToken}`;
      const userData = await api.getCurrentUser();
      setUser(userData);
      setToken(currentToken);
    } catch (err) {
      console.error('Auth verification failed:', err);
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
      delete axiosClient.defaults.headers.Authorization;
    } finally {
      setVerifying(false);
    }
  }, []);

  useEffect(() => {
    verifyAuth();
  }, [verifyAuth]);

  const login = useCallback(async (credentials) => {
    try {
      setAuthError(null);
      const response = await api.login(credentials);
      const accessToken = response.access_token || response.token;

      if (accessToken) {
        localStorage.setItem('token', accessToken);
        setToken(accessToken);
        axiosClient.defaults.headers.Authorization = `Bearer ${accessToken}`;

        await verifyAuth();
        return { success: true };
      } else {
        throw new Error('No token returned from login');
      }
    } catch (err) {
      const detail = err?.response?.data?.detail;
      // Safely handle Pydantic validation arrays (422) vs standard string errors
      const msg = Array.isArray(detail)
        ? detail.map(d => d.msg).join('; ')
        : (detail || err?.message || 'Login failed');

      setAuthError(msg);
      return { success: false, error: msg };
    }
  }, [verifyAuth]);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axiosClient.defaults.headers.Authorization;
  }, []);

  const value = {
    user,
    token,
    loading: verifying,
    verifying,
    authError,
    login,
    logout,
    verifyAuth
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
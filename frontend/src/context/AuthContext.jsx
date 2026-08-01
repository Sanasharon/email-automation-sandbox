// frontend/src/context/AuthContext.jsx
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { axiosClient } from '../api/client'; // make sure client.js exports axiosClient

const AuthContext = createContext(null);

const getHostRoot = () => {
  const configured = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  return configured.replace(/\/$/, '');
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [verifying, setVerifying] = useState(true);
  const [authError, setAuthError] = useState(null);

  const normalizeAuthResp = (resp) => {
    const body = resp?.data ?? resp;
    const token = body?.token ?? body?.access_token ?? body?.accessToken ?? null;
    const userData = body?.user ?? body?.data?.user ?? null;
    return { token, userData, body };
  };

  const verifyAuth = useCallback(async () => {
    setVerifying(true);
    setAuthError(null);
    const token = localStorage.getItem('token');
    if (!token) {
      setUser(null);
      setVerifying(false);
      return;
    }

    try {
      // Prefer the api/v1 auth verify endpoint
      const resp = await axiosClient.get('/api/v1/auth/me');
      const payload = resp?.user ?? resp ?? null;
      setUser(payload);
    } catch (err) {
      // fallback to host-root with Authorization header if necessary
      try {
        const hostRoot = getHostRoot();
        const r2 = await axios.get(`${hostRoot}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const payload = r2.data?.user ?? r2.data ?? null;
        setUser(payload);
      } catch (err2) {
        console.warn('Auth verify failed (both primary and fallback)', err, err2);
        setUser(null);
        setAuthError(err2?.message || err?.message || 'Auth verify failed');
      }
    } finally {
      setVerifying(false);
    }
  }, []);

  const login = useCallback(async (email, password) => {
    setAuthError(null);

    try {
      // Try the likely endpoint first (api/v1)
      const resp = await axiosClient.post('/api/v1/auth/login', { email, password });
      const { token, userData } = normalizeAuthResp(resp);
      if (token) {
        localStorage.setItem('token', token);
        try { axiosClient.defaults.headers.Authorization = `Bearer ${token}`; } catch {}
        setUser(userData);
        return { success: true, token, user: userData };
      }
      throw new Error('No token returned from /api/v1/auth/login');
    } catch (err) {
      // Optional fallback to host root /auth/login
      try {
        const hostRoot = getHostRoot();
        const r2 = await axios.post(`${hostRoot}/auth/login`, { email, password }, {
          headers: { 'Content-Type': 'application/json' }
        });
        const { token: token2, userData: user2 } = normalizeAuthResp(r2);
        if (token2) {
          localStorage.setItem('token', token2);
          try { axiosClient.defaults.headers.Authorization = `Bearer ${token2}`; } catch {}
          setUser(user2);
          return { success: true, token: token2, user: user2 };
        }
        setAuthError('Login did not return token');
        return { success: false, error: 'Login did not return token' };
      } catch (err2) {
        console.error('Login failed', err2);
        setAuthError(err2?.message || err?.message || 'Login failed');
        return { success: false, error: err2?.message || err?.message || 'Login failed' };
      }
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setUser(null);
    try { delete axiosClient.defaults.headers.Authorization; } catch {}
  }, []);

  useEffect(() => {
    verifyAuth();
    const onStorage = (e) => {
      if (e.key === 'token') verifyAuth();
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, [verifyAuth]);

  return (
    <AuthContext.Provider value={{ user, verifying, authError, login, logout, verifyAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
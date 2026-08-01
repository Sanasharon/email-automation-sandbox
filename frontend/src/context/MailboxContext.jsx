import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { api } from '../api/client';

const MailboxContext = createContext(null);

export const MailboxProvider = ({ children }) => {
  const [mailboxes, setMailboxes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const eventSourceRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const reconnectDelayRef = useRef(1000);

  const activeMailbox = mailboxes.length > 0 ? mailboxes[0] : null;
  const isConnected = Boolean(activeMailbox && (activeMailbox.sync_status === 'connected' || activeMailbox.sync_status === 'syncing'));
  const isSyncing = Boolean(activeMailbox && activeMailbox.sync_status === 'syncing');

  // Fetch mailboxes with a host-root fallback if the configured API path returns 404
  const fetchMailboxes = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setMailboxes([]);
      setLoading(false);
      return;
    }

    setError(null);
    setLoading(true);

    try {
      // Primary attempt via api.getMailboxes (uses axiosClient / VITE_API_BASE_URL)
      let res = await api.getMailboxes();

      // Some API clients (axiosClient interceptor) may return data directly, others a response object.
      const data = Array.isArray(res) ? res : (res?.data ?? res);

      // If the call returned HTML (e.g. dev server index.html) or not an array, handle fallback below
      if (!Array.isArray(data)) {
        // Attempt host-root fallback: derive host from configured base and call /mailboxes/ directly
        const configured = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        const hostRoot = configured.replace(/\/api\/v1\/?$/, '').replace(/\/$/, '');
        const url = `${hostRoot}/mailboxes/`;

        try {
          const r2 = await axios.get(url, { headers: { Authorization: `Bearer ${token}` } });
          const fallbackData = Array.isArray(r2.data) ? r2.data : (r2?.data ?? r2);
          setMailboxes(Array.isArray(fallbackData) ? fallbackData : []);
        } catch (fallbackErr) {
          // Fallback failed — surface original response as an error
          console.warn('Mailbox primary response not an array and fallback failed', fallbackErr);
          setMailboxes([]);
          setError('Unexpected response from mailboxes endpoint');
        }
      } else {
        setMailboxes(data);
      }
    } catch (err) {
      // If primary request returned 404, try host-root fallback explicitly
      if (err?.response?.status === 404) {
        try {
          const configured = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
          const hostRoot = configured.replace(/\/api\/v1\/?$/, '').replace(/\/$/, '');
          const url = `${hostRoot}/mailboxes/`;
          const r2 = await axios.get(url, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } });
          const fallbackData = Array.isArray(r2.data) ? r2.data : (r2?.data ?? r2);
          setMailboxes(Array.isArray(fallbackData) ? fallbackData : []);
        } catch (fallbackErr) {
          console.error('Fallback getMailboxes failed', fallbackErr);
          setMailboxes([]);
          setError('Mailboxes not found (404)');
        }
      } else {
        console.error('Failed to fetch mailboxes:', err);
        setMailboxes([]);
        setError(err?.message || 'Failed to load mailbox status');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const connectMailbox = useCallback(async () => {
    try {
      const result = await api.connectMailbox();
      await fetchMailboxes();
      return { success: true, data: result };
    } catch (err) {
      console.error('Failed to connect mailbox:', err);
      return { success: false, error: err?.message || 'Failed to connect' };
    }
  }, [fetchMailboxes]);

  const disconnectMailbox = useCallback(async (mailboxId, deleteData = false) => {
    try {
      const id = mailboxId || activeMailbox?.id;
      if (!id) throw new Error('No mailbox to disconnect');

      await api.disconnectMailbox(id, deleteData);

      // Clear state and close SSE immediately for clean UI
      setMailboxes([]);
      setError(null);
      if (eventSourceRef.current) {
        try { eventSourceRef.current.close(); } catch {}
        eventSourceRef.current = null;
      }

      return { success: true };
    } catch (err) {
      console.error('Failed to disconnect mailbox:', err);
      setMailboxes([]);
      return { success: false, error: err?.message || 'Failed to disconnect' };
    }
  }, [activeMailbox]);

  const reconnectMailbox = useCallback(async (mailboxId) => {
    try {
      const id = mailboxId || activeMailbox?.id;
      if (!id) throw new Error('No mailbox to reconnect');

      await api.reconnectMailbox(id);
      await fetchMailboxes();
      return { success: true };
    } catch (err) {
      console.error('Failed to reconnect mailbox:', err);
      return { success: false, error: err?.message || 'Failed to reconnect' };
    }
  }, [activeMailbox, fetchMailboxes]);

  const syncMailbox = useCallback(async (mailboxId) => {
    try {
      const id = mailboxId || activeMailbox?.id;
      if (!id) throw new Error('No mailbox to sync');

      await api.syncMailbox(id);
      await fetchMailboxes();
      return { success: true };
    } catch (err) {
      console.error('Failed to sync mailbox:', err);
      return { success: false, error: err?.message || 'Failed to sync' };
    }
  }, [activeMailbox, fetchMailboxes]);

  // Helper that attempts to open an EventSource and resolves when open, rejects on error/timeout.
  const tryOpenEventSource = (url, timeout = 4000) => {
    return new Promise((resolve, reject) => {
      let settled = false;
      let timer = null;
      let es = null;
      try {
        es = new EventSource(url);
      } catch (e) {
        return reject(e);
      }

      const cleanup = () => {
        if (timer) {
          clearTimeout(timer);
          timer = null;
        }
        if (es) {
          es.removeEventListener('open', onOpen);
          es.removeEventListener('error', onErr);
        }
      };

      const onOpen = () => {
        if (settled) return;
        settled = true;
        cleanup();
        resolve(es);
      };

      const onErr = (ev) => {
        if (settled) return;
        settled = true;
        cleanup();
        try { es.close(); } catch {}
        reject(new Error('EventSource error'));
      };

      es.addEventListener('open', onOpen);
      es.addEventListener('error', onErr);

      timer = setTimeout(() => {
        if (settled) return;
        settled = true;
        try { es.close(); } catch {}
        cleanup();
        reject(new Error('EventSource open timeout'));
      }, timeout);
    });
  };

  // Connect SSE with candidate URL fallback prioritizing the verified /api/v1/events/stream path
  const connectSSE = useCallback(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    // Close any existing connection and clear timers
    if (eventSourceRef.current) {
      try { eventSourceRef.current.close(); } catch {}
      eventSourceRef.current = null;
    }
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    reconnectDelayRef.current = 1000;

    const configured = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const hostRoot = configured.replace(/\/api\/v1\/?$/, '').replace(/\/$/, '');

    const candidates = [
      `${hostRoot}/api/v1/events/stream?token=${encodeURIComponent(token)}`,
      `${hostRoot}/events/stream?token=${encodeURIComponent(token)}`
    ];

    let cancelled = false;

    (async () => {
      for (const url of candidates) {
        try {
          const es = await tryOpenEventSource(url, 4000);
          if (cancelled) {
            try { es.close(); } catch {}
            return;
          }

          // Attach handlers (onmessage/onerror)
          es.onmessage = (event) => {
            try {
              const data = JSON.parse(event.data);
              switch (data.type) {
                case 'mailbox_status':
                  setMailboxes(prev => {
                    const updated = prev.map(mb =>
                      mb.id === data.mailbox_id ? { ...mb, sync_status: data.status } : mb
                    );
                    if (updated.length === 0 && data.status === 'connected') {
                      fetchMailboxes();
                    }
                    return updated;
                  });
                  break;
                case 'sync_progress':
                  setMailboxes(prev => prev.map(mb =>
                    mb.id === data.mailbox_id ? { ...mb, sync_status: 'syncing', last_sync_at: new Date().toISOString() } : mb
                  ));
                  break;
                case 'sync_complete':
                  setMailboxes(prev => prev.map(mb =>
                    mb.id === data.mailbox_id ? { ...mb, sync_status: 'connected', last_sync_at: new Date().toISOString() } : mb
                  ));
                  break;
                case 'disconnect':
                  setMailboxes([]);
                  if (eventSourceRef.current) {
                    try { eventSourceRef.current.close(); } catch {}
                    eventSourceRef.current = null;
                  }
                  break;
                default:
                  break;
              }
              // reset backoff on success
              reconnectDelayRef.current = 1000;
            } catch (e) {
              console.error('Failed to parse SSE event:', e);
            }
          };

          es.onerror = () => {
            console.warn('SSE error, scheduling reconnect');
            try { es.close(); } catch {}
            eventSourceRef.current = null;
            // Exponential backoff with a cap
            const delay = reconnectDelayRef.current;
            reconnectDelayRef.current = Math.min(delay * 2, 16000);
            reconnectTimerRef.current = setTimeout(() => {
              if (!cancelled) connectSSE();
            }, delay);
          };

          // success: keep reference and stop trying other candidates
          eventSourceRef.current = es;
          return;
        } catch (e) {
          // try next candidate
          console.warn('SSE candidate failed:', url, e);
          continue;
        }
      }

      // If we get here, none of the candidates opened
      console.warn('Could not open SSE at any candidate URL:', candidates);
      // Schedule a reconnect attempt using backoff
      const delay = reconnectDelayRef.current;
      reconnectDelayRef.current = Math.min(delay * 2, 16000);
      reconnectTimerRef.current = setTimeout(() => {
        if (!cancelled) connectSSE();
      }, delay);
    })();

    return () => {
      cancelled = true;
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
      if (eventSourceRef.current) {
        try { eventSourceRef.current.close(); } catch {}
        eventSourceRef.current = null;
      }
    };
  }, [fetchMailboxes]);

  // On mount / token change: fetch mailboxes and connect SSE (only if token present)
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setMailboxes([]);
      setLoading(false);
      if (eventSourceRef.current) {
        try { eventSourceRef.current.close(); } catch {}
        eventSourceRef.current = null;
      }
      return;
    }

    fetchMailboxes();
    const cleanup = connectSSE();

    return () => {
      if (typeof cleanup === 'function') cleanup();
      if (eventSourceRef.current) {
        try { eventSourceRef.current.close(); } catch {}
        eventSourceRef.current = null;
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };
  }, [fetchMailboxes, connectSSE]);

  const value = {
    mailboxes,
    activeMailbox,
    isConnected,
    isSyncing,
    loading,
    error,
    fetchMailboxes,
    connectMailbox,
    disconnectMailbox,
    reconnectMailbox,
    syncMailbox
  };

  return (
    <MailboxContext.Provider value={value}>
      {children}
    </MailboxContext.Provider>
  );
};

export const useMailbox = () => {
  const ctx = useContext(MailboxContext);
  if (!ctx) throw new Error('useMailbox must be used within a MailboxProvider');
  return ctx;
};

// Alias export for backward compatibility
export const useMailboxes = useMailbox;
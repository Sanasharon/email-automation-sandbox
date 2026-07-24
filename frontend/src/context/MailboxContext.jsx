import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { api } from '../api/client';

const MailboxContext = createContext(null);

export const MailboxProvider = ({ children }) => {
  const [mailboxes, setMailboxes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const eventSourceRef = useRef(null);
  const reconnectTimerRef = useRef(null);

  const activeMailbox = mailboxes.length > 0 ? mailboxes[0] : null;
  const isConnected = activeMailbox && (activeMailbox.sync_status === 'connected' || activeMailbox.sync_status === 'syncing');
  const isSyncing = activeMailbox && activeMailbox.sync_status === 'syncing';

  const fetchMailboxes = useCallback(async () => {
    try {
      setError(null);
      const res = await api.getMailboxes();
      setMailboxes(Array.isArray(res) ? res : []);
    } catch (err) {
      console.error('Failed to fetch mailboxes:', err);
      setError('Failed to load mailbox status');
      setMailboxes([]);
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
      return { success: false, error: err.message || 'Failed to connect' };
    }
  }, [fetchMailboxes]);

  const disconnectMailbox = useCallback(async (mailboxId, deleteData = false) => {
    try {
      const id = mailboxId || activeMailbox?.id;
      if (!id) throw new Error('No mailbox to disconnect');

      await api.disconnectMailbox(id, deleteData);

      // Immediately clear local state for instant UI reset
      setMailboxes([]);
      setError(null);

      // Close SSE since we're disconnected
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }

      return { success: true };
    } catch (err) {
      console.error('Failed to disconnect mailbox:', err);
      // Even if backend call fails, clear local state for clean UX
      setMailboxes([]);
      return { success: false, error: err.message || 'Failed to disconnect' };
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
      return { success: false, error: err.message || 'Failed to reconnect' };
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
      return { success: false, error: err.message || 'Failed to sync' };
    }
  }, [activeMailbox, fetchMailboxes]);

  // SSE connection with backoff
  const connectSSE = useCallback(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const eventSource = new EventSource(`${baseURL}/events/stream?token=${token}`);

    eventSourceRef.current = eventSource;
    let reconnectDelay = 1000;

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        switch (data.type) {
          case 'mailbox_status':
            setMailboxes(prev => {
              const updated = prev.map(mb =>
                mb.id === data.mailbox_id
                  ? { ...mb, sync_status: data.status }
                  : mb
              );
              if (updated.length === 0 && data.status === 'connected') {
                fetchMailboxes();
              }
              return updated;
            });
            break;
          case 'sync_progress':
            setMailboxes(prev => prev.map(mb =>
              mb.id === data.mailbox_id
                ? { ...mb, sync_status: 'syncing', last_sync_at: new Date().toISOString() }
                : mb
            ));
            break;
          case 'sync_complete':
            setMailboxes(prev => prev.map(mb =>
              mb.id === data.mailbox_id
                ? { ...mb, sync_status: 'connected', last_sync_at: new Date().toISOString() }
                : mb
            ));
            break;
          case 'disconnect':
            // Immediately clear state — no stale data
            setMailboxes([]);
            // Close SSE after disconnect
            if (eventSourceRef.current) {
              eventSourceRef.current.close();
              eventSourceRef.current = null;
            }
            break;
          default:
            break;
        }
        // Reset reconnect delay on successful message
        reconnectDelay = 1000;
      } catch (e) {
        console.error('Failed to parse SSE event:', e);
      }
    };

    eventSource.onerror = () => {
      console.warn('SSE connection error, will reconnect...');
      eventSource.close();
      eventSourceRef.current = null;
      // Backoff reconnect: 1s -> 2s -> 4s -> 8s -> 16s max
      reconnectTimerRef.current = setTimeout(() => {
        reconnectDelay = Math.min(reconnectDelay * 2, 16000);
        connectSSE();
      }, reconnectDelay);
    };

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
    };
  }, [fetchMailboxes]);

  useEffect(() => {
    fetchMailboxes();
    const cleanup = connectSSE();

    return () => {
      if (cleanup) cleanup();
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
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
  const context = useContext(MailboxContext);
  if (!context) {
    throw new Error('useMailbox must be used within a MailboxProvider');
  }
  return context;
};

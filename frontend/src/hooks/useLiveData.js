import { useState, useEffect, useCallback, useRef } from 'react';
import { useGlobalRefresh } from '../context/RefreshContext';

export const useLiveData = (fetchFn, pollingInterval = null, dependencies = []) => {
  const refreshContext = useGlobalRefresh();
  const globalRefreshKey = refreshContext ? refreshContext.refreshKey : 0;
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isPolling, setIsPolling] = useState(false);

  const fetchData = useCallback(async (isSilentPoll = false) => {
    if (!isSilentPoll) {
      setLoading(true);
    }
    setIsPolling(isSilentPoll);
    
    try {
      const fetchStartTime = Date.now();
      const result = await fetchFn();
      
      setData(prev => {
        if (!isSilentPoll || !prev) return result;
        
        const mergeArray = (prevArr, newArr) => {
          return newArr.map(newItem => {
            const prevItem = prevArr.find(p => p.id === newItem.id || p.task_id === newItem.task_id);
            if (prevItem && prevItem._lastLocalMutation && prevItem._lastLocalMutation > fetchStartTime) {
              return prevItem;
            }
            return newItem;
          });
        };
        
        if (Array.isArray(result) && Array.isArray(prev)) return mergeArray(prev, result);
        if (result?.data && Array.isArray(result.data) && prev?.data) {
          return { ...result, data: mergeArray(prev.data, result.data) };
        }
        return result;
      });
      
      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      if (!isSilentPoll) {
        setError(err.message || 'An error occurred while fetching data');
      } else {
        // For polling, we might want to track consecutive errors here
        console.error('Polling error:', err);
      }
    } finally {
      setLoading(false);
      setIsPolling(false);
    }
  }, [fetchFn]);

  useEffect(() => {
    let mounted = true;
    let pollTimer;

    const initialFetch = async () => {
      await fetchData(false);
      
      if (mounted && pollingInterval) {
        pollTimer = setInterval(() => {
          fetchData(true);
        }, pollingInterval);
      }
    };

    initialFetch();

    return () => {
      mounted = false;
      if (pollTimer) clearInterval(pollTimer);
    };
  }, [...dependencies, fetchData, pollingInterval, globalRefreshKey]);

  const refresh = () => fetchData(false);

  const updateItem = useCallback((idField, idValue, updatedFields) => {
    setData(prev => {
      const updateArray = (arr) => arr.map(item => 
        item[idField] === idValue ? { ...item, ...updatedFields, _lastLocalMutation: Date.now() } : item
      );
      
      if (Array.isArray(prev)) return updateArray(prev);
      if (prev?.data && Array.isArray(prev.data)) return { ...prev, data: updateArray(prev.data) };
      return prev;
    });
  }, []);

  const removeItem = useCallback((idField, idValue) => {
    setData(prev => {
      const filterArray = (arr) => arr.filter(item => item[idField] !== idValue);
      if (Array.isArray(prev)) return filterArray(prev);
      if (prev?.data && Array.isArray(prev.data)) return { ...prev, data: filterArray(prev.data), total: (prev.total || 1) - 1 };
      return prev;
    });
  }, []);

  const addItem = useCallback((newItem) => {
    setData(prev => {
      const itemWithMeta = { ...newItem, _lastLocalMutation: Date.now() };
      if (Array.isArray(prev)) return [itemWithMeta, ...prev];
      if (prev?.data && Array.isArray(prev.data)) return { ...prev, data: [itemWithMeta, ...prev.data], total: (prev.total || 0) + 1 };
      return prev;
    });
  }, []);

  return { data, loading, error, lastUpdated, refresh, isPolling, updateItem, removeItem, addItem };
};

import { useState, useEffect, useRef } from 'react';
import { Bell, CheckCircle2, XCircle, AlertCircle, Info } from 'lucide-react';
import { useLiveData } from '../hooks/useLiveData';
import { api } from '../api/client';

export const NotificationsDropdown = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [lastViewed, setLastViewed] = useState(() => {
    return localStorage.getItem('notifications_last_viewed') || new Date(0).toISOString();
  });
  const dropdownRef = useRef(null);

  const { data, loading } = useLiveData(api.getNotifications, 30000);
  const notifications = data || [];

  const unreadCount = notifications.filter(n => new Date(n.timestamp) > new Date(lastViewed)).length;

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleToggle = () => {
    setIsOpen(!isOpen);
    if (!isOpen && unreadCount > 0) {
      const now = new Date().toISOString();
      setLastViewed(now);
      localStorage.setItem('notifications_last_viewed', now);
    }
  };

  const handleMarkAllRead = () => {
    const now = new Date().toISOString();
    setLastViewed(now);
    localStorage.setItem('notifications_last_viewed', now);
  };

  const formatTimeAgo = (timestamp) => {
    const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  const getIcon = (type) => {
    switch(type) {
      case 'error': return <XCircle size={16} className="text-error" />;
      case 'success': return <CheckCircle2 size={16} className="text-[#1A7F37]" />;
      case 'warning': return <AlertCircle size={16} className="text-[#BF8700]" />;
      default: return <Info size={16} className="text-primary" />;
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button 
        onClick={handleToggle}
        className="relative text-on-surface-variant hover:text-primary transition-colors flex items-center justify-center p-2 rounded-full hover:bg-surface-container"
      >
        <Bell size={20} />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 w-4 h-4 bg-error text-white text-[10px] font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-surface rounded-xl shadow-lg border border-outline-variant overflow-hidden z-50">
          <div className="p-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-lowest">
            <h3 className="font-label-bold text-on-surface">Notifications</h3>
            <button onClick={handleMarkAllRead} className="text-primary text-xs font-label-bold hover:underline">
              Mark all as read
            </button>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {loading && notifications.length === 0 ? (
              <div className="p-4 text-center text-body-sm text-on-surface-variant">Loading...</div>
            ) : notifications.length === 0 ? (
              <div className="p-6 text-center text-body-sm text-on-surface-variant flex flex-col items-center">
                <Bell size={24} className="mb-2 opacity-20" />
                No recent notifications
              </div>
            ) : (
              <div className="divide-y divide-outline-variant">
                {notifications.map(n => {
                  const isUnread = new Date(n.timestamp) > new Date(lastViewed);
                  return (
                    <div key={n.id} className={`p-4 hover:bg-surface-container-lowest transition-colors flex gap-3 ${isUnread ? 'bg-primary/5' : ''}`}>
                      <div className="mt-0.5 shrink-0">{getIcon(n.type)}</div>
                      <div className="flex-1 min-w-0">
                        <p className="text-body-sm text-on-surface break-words leading-tight">{n.message}</p>
                        <p className="text-[11px] text-on-surface-variant mt-1">{formatTimeAgo(n.timestamp)}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

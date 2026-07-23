import { Menu, RefreshCw, Shield } from 'lucide-react';
import { useState } from 'react';
import { useGlobalRefresh } from '../context/RefreshContext';
import { NotificationsDropdown } from './NotificationsDropdown';
import { ApprovalQueueDrawer } from './ApprovalQueueDrawer';

export const Header = ({ title, toggleSidebar }) => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isApprovalOpen, setIsApprovalOpen] = useState(false);
  const { triggerRefresh } = useGlobalRefresh();

  const handleRefresh = () => {
    setIsRefreshing(true);
    if (triggerRefresh) triggerRefresh();
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <header className="sticky top-0 w-full h-[64px] bg-surface flex justify-between items-center px-4 md:px-8 z-30 border-b border-outline-variant">
      <div className="flex items-center">
        <button onClick={toggleSidebar} className="text-on-surface mr-4 md:hidden">
          <Menu size={24} />
        </button>
        <h1 className="font-headline-md text-headline-md font-bold text-on-surface m-0">{title}</h1>
      </div>
      <div className="flex items-center gap-4">
        <button
          onClick={() => setIsApprovalOpen(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 hover:bg-amber-100 text-xs font-semibold border border-amber-200 dark:border-amber-800 transition-all"
          title="Open AI Approval Queue"
        >
          <Shield size={14} className="text-amber-600" />
          <span>Approval Queue</span>
        </button>

        <button 
          onClick={handleRefresh}
          className="text-on-surface-variant hover:text-primary transition-colors active:scale-95 flex items-center justify-center" 
          title="Refresh Data"
        >
          <RefreshCw size={20} className={isRefreshing ? 'animate-spin' : ''} />
        </button>
        <NotificationsDropdown />
        <div className="flex items-center gap-2 px-3 py-1 bg-surface-container rounded-lg">
          <span className="w-2 h-2 bg-[#1A7F37] rounded-full animate-pulse"></span>
          <span className="text-label-bold text-on-surface-variant tracking-wider">SYSTEM LIVE</span>
        </div>
      </div>

      <ApprovalQueueDrawer isOpen={isApprovalOpen} onClose={() => setIsApprovalOpen(false)} />
    </header>
  );
};

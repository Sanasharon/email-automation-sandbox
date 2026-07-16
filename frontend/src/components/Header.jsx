import { Menu, RefreshCw } from 'lucide-react';
import { useState } from 'react';
import { useGlobalRefresh } from '../context/RefreshContext';

export const Header = ({ title, toggleSidebar }) => {
  const [isRefreshing, setIsRefreshing] = useState(false);
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
          onClick={handleRefresh}
          className="text-on-surface-variant hover:text-primary transition-colors active:scale-95 flex items-center justify-center" 
          title="Refresh Data"
        >
          <RefreshCw size={20} className={isRefreshing ? 'animate-spin' : ''} />
        </button>
        <div className="flex items-center gap-2 px-3 py-1 bg-surface-container rounded-lg">
          <span className="w-2 h-2 bg-[#1A7F37] rounded-full animate-pulse"></span>
          <span className="text-label-bold text-on-surface-variant tracking-wider">SYSTEM LIVE</span>
        </div>
      </div>
    </header>
  );
};

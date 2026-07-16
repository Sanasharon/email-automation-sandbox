import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { Header } from '../components/Header';

export const MainLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const getPageTitle = (pathname) => {
    switch (pathname) {
      case '/': return 'Dashboard Overview';
      case '/workflows': return 'Workflow Control';
      case '/monitoring': return 'Email Monitoring';
      case '/automation': return 'Automation Activity';
      default: return 'Control Panel';
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Sidebar isOpen={sidebarOpen} toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      
      <div className="md:ml-[260px] flex-1 flex flex-col relative">
        <Header 
          title={getPageTitle(location.pathname)} 
          toggleSidebar={() => setSidebarOpen(!sidebarOpen)} 
        />
        
        <main className="flex-1 p-6 md:p-8 max-w-[1280px] mx-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

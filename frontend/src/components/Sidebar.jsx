import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Menu } from 'lucide-react';

export const Sidebar = ({ isOpen, toggleSidebar }) => {
  const mainNavItems = [
    { name: 'Dashboard', path: '/', icon: 'dashboard' },
    { name: 'Workflows', path: '/workflows', icon: 'account_tree' },
    { name: 'Email Monitoring', path: '/monitoring', icon: 'mail' },
    { name: 'Automation', path: '/automation', icon: 'settings_suggest' },
  ];


  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={toggleSidebar}
        />
      )}
      
      <aside className={`fixed left-0 top-0 h-full w-[260px] bg-inverse-surface flex flex-col overflow-y-auto border-r border-outline-variant z-50 transition-transform duration-300 ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="px-6 py-8">
          <div className="mb-8">
            <div className="flex items-baseline font-display-lg text-[32px] font-bold tracking-tight">
              <span className="text-[#2563EB]">UT</span>
              <span className="text-white">SERVIO</span>
            </div>
            <span className="text-[12px] text-surface-variant tracking-wide block mt-1">AI Email Automation</span>
          </div>
          <nav className="space-y-1">
            {mainNavItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => 
                  `flex items-center px-4 py-3 transition-colors active:opacity-80 ${
                    isActive 
                      ? 'text-on-primary font-label-bold border-l-2 border-primary bg-secondary-container/10' 
                      : 'text-surface-variant font-label-md hover:bg-surface-container-highest hover:text-on-surface border-l-2 border-transparent'
                  }`
                }
                onClick={() => {
                  if (window.innerWidth < 768) toggleSidebar();
                }}
              >
                <span className="material-symbols-outlined mr-3 text-[20px]">{item.icon}</span>
                <span>{item.name}</span>
              </NavLink>
            ))}


          </nav>
        </div>
        <div className="mt-auto px-6 py-6 border-t border-white/10">
          {/* TODO: Bind to real authenticated user object once auth is integrated. (Currently hardcoded) */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-container rounded-full flex items-center justify-center text-on-primary font-bold">
              AU
            </div>
            <div>
              <p className="text-white font-label-bold text-label-md">Admin User</p>
              <p className="text-surface-variant text-[11px]">Enterprise Plan</p>
            </div>
          </div>
          <div className="mt-4 text-surface-variant text-[10px] uppercase tracking-widest font-bold">
            v2.4.0
          </div>
        </div>
      </aside>
    </>
  );
};

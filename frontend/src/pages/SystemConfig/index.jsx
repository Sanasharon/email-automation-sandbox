import React from 'react';
import { Settings as SettingsIcon, Shield, Server, Bell, Key } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const SystemConfig = () => {
  const { user } = useAuth();
  
  if (user?.role !== 'Admin') {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <Shield className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Access Denied</h2>
        <p className="text-gray-500 mt-2">You don't have permission to perform this action.</p>
      </div>
    );
  }

  const sections = [
    { title: 'General System Settings', icon: <Server className="w-5 h-5 text-gray-500" />, desc: 'Configure global application parameters.' },
    { title: 'API Keys & Secrets', icon: <Key className="w-5 h-5 text-gray-500" />, desc: 'Manage OpenAI and Supabase credentials.' },
    { title: 'Notifications', icon: <Bell className="w-5 h-5 text-gray-500" />, desc: 'System alert and email notification preferences.' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-gray-600 dark:text-gray-400" />
          System Settings
        </h1>
        <p className="text-sm text-gray-500 mt-1">Manage global configuration for the email automation engine.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-2">
          {sections.map((sec, idx) => (
            <div key={idx} className={`p-4 rounded-xl cursor-pointer flex items-start gap-3 transition-colors ${idx === 0 ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800' : 'hover:bg-gray-50 dark:hover:bg-gray-800 border border-transparent'}`}>
              <div className="mt-0.5">{sec.icon}</div>
              <div>
                <h3 className={`text-sm font-bold ${idx === 0 ? 'text-blue-700 dark:text-blue-400' : 'text-gray-900 dark:text-white'}`}>{sec.title}</h3>
                <p className="text-xs text-gray-500 mt-1">{sec.desc}</p>
              </div>
            </div>
          ))}
        </div>
        
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-6 border-b border-gray-200 dark:border-gray-700 pb-4">General System Settings</h2>
          
          <form className="space-y-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Application Name</label>
                <input type="text" defaultValue="Utservio Dashboard" className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Support Email</label>
                <input type="email" defaultValue="support@utservio.com" className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
              </div>
              
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">Maintenance Mode</h4>
                  <p className="text-xs text-gray-500">Temporarily disable system access for non-admins.</p>
                </div>
                <div className="relative inline-block w-10 h-6 cursor-pointer">
                  <input type="checkbox" className="sr-only peer" />
                  <div className="w-10 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                </div>
              </div>
            </div>
            
            <div className="flex justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
              <button type="button" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                Save Changes
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SystemConfig;

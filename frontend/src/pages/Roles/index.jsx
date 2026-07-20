import React from 'react';
import { Shield, Plus, Settings } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Roles = () => {
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

  const dummyRoles = [
    { id: 1, name: 'Admin', users: 1, description: 'Full system access including user management.' },
    { id: 2, name: 'Editor', users: 3, description: 'Can manage workflows and templates.' },
    { id: 3, name: 'Viewer', users: 12, description: 'Read-only access to monitoring and logs.' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Shield className="w-6 h-6 text-purple-600" />
            Roles & Permissions
          </h1>
          <p className="text-sm text-gray-500 mt-1">Define access levels for system users.</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" />
          Create Role
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dummyRoles.map(role => (
          <div key={role.id} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 flex flex-col hover:border-purple-300 dark:hover:border-purple-700 transition-colors cursor-pointer group">
            <div className="flex justify-between items-start mb-4">
              <div className="w-12 h-12 rounded-lg bg-purple-50 dark:bg-purple-900/20 flex items-center justify-center text-purple-600 dark:text-purple-400 group-hover:scale-110 transition-transform">
                <Shield className="w-6 h-6" />
              </div>
              <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                <Settings className="w-5 h-5" />
              </button>
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">{role.name}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-6 flex-1">{role.description}</p>
            <div className="pt-4 border-t border-gray-100 dark:border-gray-700/50 flex justify-between items-center text-sm font-medium text-gray-700 dark:text-gray-300">
              <span>Users Assigned</span>
              <span className="bg-gray-100 dark:bg-gray-700 px-2.5 py-1 rounded-md">{role.users}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Roles;

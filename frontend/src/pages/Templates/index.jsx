import React from 'react';
import { FileText, Plus, Shield } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Templates = () => {
  const { user } = useAuth();
  const [templates, setTemplates] = React.useState([]);
  const [showModal, setShowModal] = React.useState(false);
  const [newTemplateName, setNewTemplateName] = React.useState('');
  const [newTemplateContent, setNewTemplateContent] = React.useState('');
  
  if (user?.role !== 'Admin' && user?.role !== 'Editor') {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <Shield className="w-16 h-16 text-red-500 mb-4" />
        <h2 className="text-xl font-bold text-gray-900 dark:text-white">Access Denied</h2>
        <p className="text-gray-500 mt-2">You don't have permission to perform this action.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <FileText className="w-6 h-6 text-indigo-600" />
            Response Templates
          </h1>
          <p className="text-sm text-gray-500 mt-1">Manage automated email response templates.</p>
        </div>
        <button onClick={() => setShowModal(true)} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" />
          Create Template
        </button>
      </div>

      {templates.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-12 flex flex-col items-center text-center">
          <div className="w-16 h-16 bg-gray-50 dark:bg-gray-900 rounded-full flex items-center justify-center mb-4">
            <FileText className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">No templates found</h3>
          <p className="text-gray-500 max-w-sm mb-6">You haven't created any automated response templates yet. Create your first template to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {templates.map(t => (
            <div key={t.id} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">{t.name}</h3>
              <div className="prose dark:prose-invert" dangerouslySetInnerHTML={{ __html: t.content }} />
            </div>
          ))}
        </div>
      )}

    </div>
  );
};

export default Templates;

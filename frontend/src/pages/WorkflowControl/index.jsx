import { useState, useEffect, useCallback } from 'react';
import { useLiveData } from '../../hooks/useLiveData';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../api/client';
import { DataTable } from '../../components/DataTable';
import { FilterTabs } from '../../components/FilterTabs';
import { SearchBar } from '../../components/SearchBar';
import { StatusBadge } from '../../components/StatusBadge';
import { Modal } from '../../components/Modal';
import { ConfirmDialog } from '../../components/ConfirmDialog';
import { LoadingSkeleton } from '../../components/LoadingSkeleton';
import { EmptyState } from '../../components/EmptyState';
import { Plus, Play, Square, Settings, Trash2, Edit2, Check, X } from 'lucide-react';

export const WorkflowControl = () => {
  const { canEdit } = useAuth();
  const [activeTab, setActiveTab] = useState('all');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [editingWorkflow, setEditingWorkflow] = useState(null);
  const [deletingWorkflow, setDeletingWorkflow] = useState(null);
  const [formData, setFormData] = useState({ name: '', trigger_type: 'webhook', schedule: '', category_filter: '', destination_team: '' });
  const [formError, setFormError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchWorkflows = useCallback(() => api.getWorkflows({ status: 'all', search, page, pageSize }), [search, page, pageSize]);
  const { data, loading, error, addItem, updateItem, removeItem } = useLiveData(fetchWorkflows, null, [fetchWorkflows]);
  
  // Client-side filtering by status to avoid re-fetch on tab change
  const filteredData = data?.data ? (activeTab === 'all' ? data.data : data.data.filter(w => w.status === activeTab)) : [];
  const totalFiltered = data?.data ? (activeTab === 'all' ? data.total : filteredData.length) : 0;
  
  const { data: categoriesData } = useLiveData(api.getCategories, null, []);

  const handleCreateEdit = async () => {
    setFormError(null);
    if (!formData.name || formData.name.trim().length === 0) {
      setFormError('Workflow name is required.');
      return;
    }
    if (formData.name.length > 100) {
      setFormError('Workflow name must be under 100 characters.');
      return;
    }
    
    // Sanitize input: React escapes automatically on render, but we can strip potentially harmful tags.
    const sanitizedData = {
      ...formData,
      name: formData.name.replace(/</g, "&lt;").replace(/>/g, "&gt;")
    };
    
    setIsSubmitting(true);
    try {
      if (editingWorkflow) {
        const updated = await api.updateWorkflow(editingWorkflow.id, sanitizedData);
        updateItem('id', editingWorkflow.id, updated);
      } else {
        const created = await api.createWorkflow(sanitizedData);
        addItem(created);
      }
      setIsModalOpen(false);
    } catch (err) {
      setFormError('Failed to save workflow. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    try {
      await api.deleteWorkflow(deletingWorkflow.id);
      removeItem('id', deletingWorkflow.id);
      setIsDeleteDialogOpen(false);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAction = async (id, action) => {
    try {
      const updated = await api.toggleWorkflowState(id, action);
      updateItem('id', id, updated);
    } catch (err) {
      console.error(err);
    }
  };

  const columns = [
    { header: 'Workflow Name', accessor: 'name', cellClassName: 'font-medium text-on-surface' },
    { header: 'Status', accessor: 'status', render: (row) => <StatusBadge status={row.status} /> },
    { header: 'Trigger', accessor: 'trigger_type', render: (row) => <span className="uppercase text-xs">{row.trigger_type}</span> },
    { header: 'Last Run', accessor: 'last_run', render: (row) => row.last_run ? new Date(row.last_run).toLocaleString() : 'Never' },
    { header: 'Actions', render: (row) => (
      <div className="flex gap-2">
        {row.status === 'running' ? (
          <button onClick={() => handleAction(row.id, 'stop')} className="text-on-surface-variant hover:text-error transition-colors" title="Stop">
            <Square size={16} />
          </button>
        ) : row.status === 'active' ? (
          <button onClick={() => handleAction(row.id, 'start')} className="text-on-surface-variant hover:text-[#1A7F37] transition-colors" title="Start">
            <Play size={16} />
          </button>
        ) : (
          <button onClick={() => handleAction(row.id, 'enable')} className="text-on-surface-variant hover:text-[#1A7F37] transition-colors" title="Enable">
            <Check size={16} />
          </button>
        )}
        {(row.status === 'active' || row.status === 'running') && (
           <button onClick={() => handleAction(row.id, 'disable')} className="text-on-surface-variant hover:text-error transition-colors" title="Disable">
             <X size={16} />
           </button>
        )}
        {canEdit && (
          <>
            <button onClick={() => {
              setEditingWorkflow(row);
              setFormData({
                name: row.name,
                trigger_type: row.trigger_type,
                schedule: row.schedule || '',
                category_filter: row.category_filter || '',
                destination_team: row.destination_team || ''
              });
              setIsModalOpen(true);
            }} className="text-on-surface-variant hover:text-primary transition-colors" title="Edit">
              <Edit2 size={16} />
            </button>
            <button onClick={() => {
              setDeletingWorkflow(row);
              setIsDeleteDialogOpen(true);
            }} className="text-on-surface-variant hover:text-error transition-colors" title="Delete">
              <Trash2 size={16} />
            </button>
          </>
        )}
      </div>
    ) }
  ];

  const tabs = [
    { id: 'all', label: 'All Workflows' },
    { id: 'running', label: 'Running' },
    { id: 'active', label: 'Active' },
    { id: 'paused', label: 'Paused' },
    { id: 'disabled', label: 'Disabled' }
  ];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <FilterTabs tabs={tabs} activeTab={activeTab} onChange={(id) => { setActiveTab(id); setPage(1); }} />
        <div className="flex gap-4 w-full sm:w-auto">
          <SearchBar onSearch={(q) => { setSearch(q); setPage(1); }} placeholder="Search workflows..." />
          {canEdit && (
            <button 
              onClick={() => {
                setEditingWorkflow(null);
                setFormData({ name: '', trigger_type: 'webhook', schedule: '', category_filter: '', destination_team: '' });
                setIsModalOpen(true);
              }}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-on-primary rounded-md font-medium text-body-md hover:bg-primary/90 transition-colors whitespace-nowrap"
            >
              <Plus size={18} />
              <span>Create</span>
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-error-container text-on-error-container p-4 rounded-md text-body-md">
          {error}
        </div>
      )}

      <div className="flat-card overflow-hidden">
        <DataTable
          columns={columns}
          data={filteredData}
          page={page}
          pageSize={pageSize}
          total={totalFiltered}
          onPageChange={setPage}
          loading={loading}
          loadingSkeleton={<LoadingSkeleton type="table" rows={5} />}
          emptyState={<EmptyState message="No workflows found matching your criteria." actionText="Create Workflow" onAction={() => setIsModalOpen(true)} />}
        />
      </div>

      <Modal 
        isOpen={isModalOpen} 
        onClose={() => !isSubmitting && setIsModalOpen(false)} 
        title={editingWorkflow ? 'Edit Workflow' : 'Create Workflow'}
      >
        <div className="flex flex-col gap-4 py-2">
          {formError && <div className="text-error text-body-md p-2 bg-error-container/20 rounded">{formError}</div>}
          
          <div className="flex flex-col gap-1">
            <label className="text-label-bold text-on-surface-variant">Name</label>
            <input 
              type="text" 
              value={formData.name} 
              onChange={e => setFormData({...formData, name: e.target.value})} 
              className="px-3 py-2 border border-outline-variant rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
              disabled={isSubmitting}
            />
          </div>
          
          <div className="flex flex-col gap-1">
            <label className="text-label-bold text-on-surface-variant">Trigger Type</label>
            <select 
              value={formData.trigger_type} 
              onChange={e => setFormData({...formData, trigger_type: e.target.value})}
              className="px-3 py-2 border border-outline-variant rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
              disabled={isSubmitting}
            >
              <option value="webhook">Webhook</option>
              <option value="cron">Cron Schedule</option>
              <option value="api_poll">API Poll</option>
              <option value="manual">Manual</option>
            </select>
          </div>

          {formData.trigger_type === 'cron' && (
            <div className="flex flex-col gap-1">
              <label className="text-label-bold text-on-surface-variant">Schedule (Cron)</label>
              <input 
                type="text" 
                value={formData.schedule} 
                onChange={e => setFormData({...formData, schedule: e.target.value})} 
                placeholder="*/10 * * * *"
                className="px-3 py-2 border border-outline-variant rounded-md focus:outline-none focus:ring-1 focus:ring-primary font-mono"
                disabled={isSubmitting}
              />
            </div>
          )}

          <div className="flex flex-col gap-1">
            <label className="text-label-bold text-on-surface-variant">Category Filter</label>
            <select 
              value={formData.category_filter} 
              onChange={e => {
                const cat = categoriesData?.data?.find(c => c.category === e.target.value);
                setFormData({...formData, category_filter: e.target.value, destination_team: cat ? cat.department : ''});
              }}
              className="px-3 py-2 border border-outline-variant rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
              disabled={isSubmitting}
            >
              <option value="">Any Category</option>
              {categoriesData?.data?.map(c => (
                <option key={c.category} value={c.category}>{c.category}</option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-label-bold text-on-surface-variant">Destination Team</label>
            <input 
              type="text" 
              value={formData.destination_team} 
              readOnly 
              className="px-3 py-2 border border-outline-variant rounded-md bg-surface-container-low text-on-surface-variant cursor-not-allowed"
            />
            <span className="text-[10px] text-on-surface-variant">Auto-filled based on category routing matrix</span>
          </div>

          <div className="flex justify-end gap-3 mt-4">
            <button onClick={() => setIsModalOpen(false)} disabled={isSubmitting} className="px-4 py-2 border border-outline-variant rounded-md text-on-surface-variant hover:bg-surface-container-highest">Cancel</button>
            <button onClick={handleCreateEdit} disabled={isSubmitting} className="px-4 py-2 bg-primary text-on-primary rounded-md hover:bg-primary/90 disabled:opacity-70">
              {isSubmitting ? 'Saving...' : 'Save Workflow'}
            </button>
          </div>
        </div>
      </Modal>

      <ConfirmDialog 
        isOpen={isDeleteDialogOpen} 
        onClose={() => setIsDeleteDialogOpen(false)}
        title="Delete Workflow"
        message={`Are you sure you want to delete "${deletingWorkflow?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        isDestructive={true}
        onConfirm={handleDelete}
      />
    </div>
  );
};

import { useState, useCallback } from 'react';
import { useLiveData } from '../../hooks/useLiveData';
import { api } from '../../api/client';
import { DataTable } from '../../components/DataTable';
import { FilterTabs } from '../../components/FilterTabs';
import { SearchBar } from '../../components/SearchBar';
import { StatusBadge } from '../../components/StatusBadge';
import { LoadingSkeleton } from '../../components/LoadingSkeleton';
import { EmptyState } from '../../components/EmptyState';
import { RotateCcw, Download, AlertCircle, Eye, CheckCircle, Clock } from 'lucide-react';
import { getStatusConfig } from '../../config/statusConfig';
import { useAuth } from '../../context/AuthContext';
import { EmailDetailDrawer } from '../../components/EmailDetailDrawer';

export const EmailMonitoring = () => {
  const { canEdit } = useAuth();
  const [activeTab, setActiveTab] = useState('all');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  
  const [retryingId, setRetryingId] = useState(null);
  const [actionError, setActionError] = useState(null);
  
  const [isExportingAll, setIsExportingAll] = useState(false);
  const [isExportingFiltered, setIsExportingFiltered] = useState(false);
  const [selectedEmailId, setSelectedEmailId] = useState(null);

  const fetchEmails = useCallback(() => api.getEmails({ status: activeTab, search, page, pageSize }), [activeTab, search, page, pageSize]);
  const fetchStats = useCallback(() => api.getEmailStats(), []);

  const { data, loading, error, refresh, updateItem } = useLiveData(fetchEmails, 5000, [fetchEmails]);
  const { data: stats } = useLiveData(fetchStats, 5000, [fetchStats]);

  const filteredData = data?.data || [];
  const totalFiltered = data?.total || 0;

  const handleRetry = async (id) => {
    setRetryingId(id);
    setActionError(null);
    try {
      const updated = await api.retryEmail(id);
      updateItem('id', id, updated);
    } catch (err) {
      setActionError(`Failed to retry email ${id}`);
    } finally {
      setRetryingId(null);
    }
  };

  const handleExport = async (type) => {
    setActionError(null);
    if (type === 'all') {
      setIsExportingAll(true);
      try {
        await api.exportEmails('all', '');
      } catch (err) {
        setActionError('Failed to export all emails.');
      } finally {
        setIsExportingAll(false);
      }
    } else {
      setIsExportingFiltered(true);
      try {
        await api.exportEmails(activeTab, search);
      } catch (err) {
        setActionError('Failed to export filtered emails.');
      } finally {
        setIsExportingFiltered(false);
      }
    }
  };

  const columns = [
    { header: 'Sender', accessor: 'sender', cellClassName: 'font-medium text-on-surface' },
    { header: 'Subject', accessor: 'subject', render: (row) => <div className="max-w-[200px] truncate" title={row.subject}>{row.subject}</div> },
    { header: 'Category', accessor: 'category', render: (row) => <span className="text-on-surface-variant bg-surface-container px-2 py-1 rounded text-xs">{row.category}</span> },
    { header: 'Workflow', accessor: 'workflow_name', render: (row) => <div className="max-w-[150px] truncate text-primary font-medium" title={row.workflow_name}>{row.workflow_name}</div> },
    { 
      header: 'AI Generated', 
      render: (row) => (
        <span className={`px-2 py-0.5 rounded text-xs font-semibold ${row.has_ai_draft ? 'bg-indigo-100 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300' : 'bg-gray-100 text-gray-500'}`}>
          {row.has_ai_draft ? 'Yes' : 'No'}
        </span>
      )
    },
    { 
      header: 'Approval Status', 
      render: (row) => {
        if (!row.approval_status) return <span className="text-gray-400 text-xs">N/A</span>;
        return (
          <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
            row.approval_status === 'approved' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'
          }`}>
            {row.approval_status === 'approved' ? 'Approved' : 'Pending Review'}
          </span>
        );
      }
    },
    { header: 'Status', accessor: 'status', render: (row) => <StatusBadge status={row.status} /> },
    { header: 'Sent Time', accessor: 'sent_time', render: (row) => new Date(row.sent_time).toLocaleString() },
    { header: 'Actions', render: (row) => (
        <div className="flex gap-2 min-w-[80px]">
          <button 
            onClick={() => setSelectedEmailId(row.id)} 
            className="flex items-center gap-1 text-[11px] px-2 py-1 border border-outline-variant rounded transition-colors text-on-surface hover:bg-surface-container-high"
          >
            <Eye size={12} />
            View Details
          </button>
        </div>
      )
    }
  ];

  // Note: This module currently reflects inbound collection status only.
  // Outbound send-tracking (Sent/Delivered/Bounced) is a planned future capability 
  // and should extend this same config pattern, not replace it.
  const tabs = [
    { id: 'all', label: 'All Emails', statKey: 'total' },
    { id: 'collected', label: 'Collected', statKey: 'collected' },
    { id: 'completed', label: 'Completed', statKey: 'completed' },
    { id: 'failed', label: 'Failed', statKey: 'failed' }
  ];

  return (
    <div className="flex flex-col gap-6 relative">
      
      {/* Live Status Indicator */}
      <div className="absolute -top-12 right-0 flex items-center gap-2 text-xs">
        {error ? (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-error-container text-on-error-container">
            <AlertCircle size={14} />
            <span>Backend Offline</span>
          </div>
        ) : loading && !data ? (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-container-high text-on-surface-variant">
            <RotateCcw size={14} className="animate-spin" />
            <span>Waiting for Backend...</span>
          </div>
        ) : (
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#DAFBE1] text-[#1A7F37] border border-[#1A7F37]/20">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#1A7F37] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#1A7F37]"></span>
            </span>
            <span className="font-medium">Live</span>
          </div>
        )}
      </div>
      
      {/* Dynamic KPI Cards driven by the tabs configuration */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {tabs.map(tab => {
          // stats backend returns collected, parsed, completed, failed
          // We combine parsed + completed into "completed" stat here if needed,
          // but if backend endpoint returned exact keys, use those.
          let count = 0;
          if (stats) {
            if (tab.statKey === 'completed') {
               count = (stats['completed'] || 0) + (stats['parsed'] || 0);
            } else {
               count = stats[tab.statKey] || 0;
            }
          }
          
          return (
            <div key={tab.id} className="flat-card flex flex-col items-center justify-center p-4">
              <span className="text-on-surface-variant text-sm font-medium uppercase tracking-wider">{tab.label}</span>
              <span className="text-3xl font-bold text-primary mt-1">{count}</span>
            </div>
          );
        })}
      </div>

      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <FilterTabs tabs={tabs} activeTab={activeTab} onChange={(id) => { setActiveTab(id); setPage(1); }} />
        <div className="w-full sm:w-auto flex flex-col sm:flex-row gap-3 items-start sm:items-center">
          <SearchBar onSearch={(q) => { setSearch(q); setPage(1); }} placeholder="Search sender or subject..." />
          
          {canEdit && (
            <div className="flex gap-2 items-center group relative">
              <button 
                onClick={() => handleExport('filtered')}
                disabled={isExportingFiltered || isExportingAll}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-surface-container-high text-on-surface-variant hover:text-primary rounded text-sm font-medium border border-outline-variant hover:border-primary disabled:opacity-50 transition-colors"
                title="Export currently filtered view"
              >
                {isExportingFiltered ? <RotateCcw size={14} className="animate-spin" /> : <Download size={14} />}
                {isExportingFiltered ? 'Exporting...' : 'Export Filtered'}
              </button>
              
              <button 
                onClick={() => handleExport('all')}
                disabled={isExportingFiltered || isExportingAll}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-on-primary hover:bg-primary/90 rounded text-sm font-medium disabled:opacity-50 transition-colors"
                title="Export all database records"
              >
                {isExportingAll ? <RotateCcw size={14} className="animate-spin" /> : <Download size={14} />}
                {isExportingAll ? 'Exporting...' : 'Export All'}
              </button>
              
              <AlertCircle size={16} className="text-on-surface-variant/70 hover:text-error cursor-help" />
              <div className="absolute top-full right-0 mt-2 w-64 p-2 bg-inverse-surface text-inverse-on-surface text-xs rounded shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10 pointer-events-none">
                Exports include full email content — handle exported files according to company data policy.
              </div>
            </div>
          )}
        </div>
      </div>

      {(error || actionError) && (
        <div className="bg-error-container text-on-error-container p-4 rounded-md text-body-md flex justify-between items-center">
          <span>{error || actionError}</span>
          {error && <button onClick={refresh} className="underline text-sm font-bold">Retry Fetch</button>}
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
          onPageSizeChange={(newSize) => { setPageSize(newSize); setPage(1); }}
          loading={loading}
          loadingSkeleton={<LoadingSkeleton type="table" rows={10} />}
          emptyState={<EmptyState message={`No ${activeTab !== 'all' ? activeTab : ''} emails found.`} />}
        />
      </div>
      
      {selectedEmailId && (
        <EmailDetailDrawer 
          emailId={selectedEmailId} 
          onClose={() => setSelectedEmailId(null)} 
        />
      )}
    </div>
  );
};

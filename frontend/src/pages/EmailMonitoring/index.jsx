import { useState, useCallback } from 'react';
import { useLiveData } from '../../hooks/useLiveData';
import { api } from '../../api/client';
import { DataTable } from '../../components/DataTable';
import { FilterTabs } from '../../components/FilterTabs';
import { SearchBar } from '../../components/SearchBar';
import { StatusBadge } from '../../components/StatusBadge';
import { LoadingSkeleton } from '../../components/LoadingSkeleton';
import { EmptyState } from '../../components/EmptyState';
import { RotateCcw } from 'lucide-react';

export const EmailMonitoring = () => {
  const [activeTab, setActiveTab] = useState('all');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;
  
  const [retryingId, setRetryingId] = useState(null);
  const [actionError, setActionError] = useState(null);

  const fetchEmails = useCallback(() => api.getEmails({ status: 'all', search, page, pageSize }), [search, page, pageSize]);
  const { data, loading, error, refresh, updateItem } = useLiveData(fetchEmails, null, [fetchEmails]);

  // Client-side filtering by status to avoid re-fetch on tab change
  const filteredData = data?.data ? (activeTab === 'all' ? data.data : data.data.filter(e => e.status === activeTab)) : [];
  const totalFiltered = data?.data ? (activeTab === 'all' ? data.total : filteredData.length) : 0;

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

  const columns = [
    { header: 'Recipient', accessor: 'recipient', cellClassName: 'font-medium text-on-surface' },
    { header: 'Subject', accessor: 'subject', render: (row) => <div className="max-w-[300px] truncate" title={row.subject}>{row.subject}</div> },
    { header: 'Category', accessor: 'category', render: (row) => <span className="text-on-surface-variant bg-surface-container px-2 py-1 rounded text-xs">{row.category}</span> },
    { header: 'Status', accessor: 'status', render: (row) => <StatusBadge status={row.status} /> },
    { header: 'Sent Time', accessor: 'sent_time', render: (row) => new Date(row.sent_time).toLocaleString() },
    { header: 'Actions', render: (row) => (
      <div className="flex gap-2 min-w-[80px]">
        {row.status === 'failed' && (
          <button 
            onClick={() => handleRetry(row.id)} 
            disabled={retryingId === row.id}
            className={`flex items-center gap-1 text-[11px] px-2 py-1 border rounded transition-colors ${
              retryingId === row.id ? 'opacity-50 border-outline-variant text-on-surface-variant' : 'border-[#1A7F37] text-[#1A7F37] hover:bg-[#DAFBE1]'
            }`}
          >
            <RotateCcw size={12} className={retryingId === row.id ? 'animate-spin' : ''} />
            {retryingId === row.id ? 'Retrying' : 'Retry'}
          </button>
        )}
      </div>
    )}
  ];

  const tabs = [
    { id: 'all', label: 'All Emails' },
    { id: 'sent', label: 'Sent' },
    { id: 'delivered', label: 'Delivered' },
    { id: 'pending', label: 'Pending' },
    { id: 'failed', label: 'Failed' },
    { id: 'bounced', label: 'Bounced' }
  ];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <FilterTabs tabs={tabs} activeTab={activeTab} onChange={(id) => { setActiveTab(id); setPage(1); }} />
        <div className="w-full sm:w-auto">
          <SearchBar onSearch={(q) => { setSearch(q); setPage(1); }} placeholder="Search recipient or subject..." />
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
          loading={loading}
          loadingSkeleton={<LoadingSkeleton type="table" rows={10} />}
          emptyState={<EmptyState message={`No ${activeTab !== 'all' ? activeTab : ''} emails found.`} />}
        />
      </div>
    </div>
  );
};

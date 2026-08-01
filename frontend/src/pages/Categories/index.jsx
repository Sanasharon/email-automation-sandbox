import { useState, useCallback } from 'react';
import { useLiveData } from '../../hooks/useLiveData';
import { api } from '../../api/client';
import { DataTable } from '../../components/DataTable';
import { EmptyState } from '../../components/EmptyState';
import { LoadingSkeleton } from '../../components/LoadingSkeleton';

const PriorityBadge = ({ priority }) => {
  const styles = {
    high: 'bg-error-container text-on-error-container',
    medium: 'bg-[#FFF8C5] text-[#9A6700]',
    low: 'bg-[#DAFBE1] text-[#1A7F37]',
    unset: 'bg-surface-variant text-on-surface-variant',
  };
  return (
    <span className={`text-[10px] px-2 py-0.5 font-bold rounded-full uppercase tracking-widest ${styles[priority] || styles.unset}`}>
      {priority}
    </span>
  );
};

export const Categories = () => {
  const [activeCategory, setActiveCategory] = useState('All');
  const [search, setSearch] = useState('');
  const [sortDir, setSortDir] = useState('desc');
  const [page, setPage] = useState(1);
  const pageSize = 25;

  const fetchCounts = useCallback(() => api.getCategoryCounts(), []);
  const { data: countsData } = useLiveData(fetchCounts, 15000, []);

  const fetchEmails = useCallback(
    () => api.getEmailsByCategory({
      category: activeCategory,
      search,
      sort: sortDir,
      skip: (page - 1) * pageSize,
      limit: pageSize,
    }),
    [activeCategory, search, sortDir, page]
  );
  const { data, loading, error } = useLiveData(fetchEmails, 10000, [fetchEmails]);

  const categories = countsData?.categories || {};
  const categoryList = ['All', ...Object.keys(categories)];
  const rows = data?.data || [];
  const total = data?.total || 0;

  const columns = [
    { header: 'Category', accessor: 'category' },
    {
      header: (
        <button
          type="button"
          onClick={() => setSortDir((d) => (d === 'desc' ? 'asc' : 'desc'))}
          className="flex items-center gap-1"
        >
          Priority {sortDir === 'desc' ? '↓' : '↑'}
        </button>
      ),
      accessor: 'priority',
      render: (row) => <PriorityBadge priority={row.priority} />,
    },
    { header: 'Subject', accessor: 'subject' },
    { header: 'Sender', accessor: 'sender' },
    { header: 'Received', accessor: 'received_at', render: (row) => row.received_at ? new Date(row.received_at).toLocaleString() : '—' },
    { header: 'Status', accessor: 'status' },
  ];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-display-lg font-display-lg text-on-surface">Categories &amp; Priority</h1>
        <p className="text-body-md text-on-surface-variant mt-1">Browse synced emails grouped by category, sorted by priority.</p>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          {categoryList.map((c) => (
            <button
              key={c}
              onClick={() => { setActiveCategory(c); setPage(1); }}
              className={`px-3 py-1.5 rounded-full text-label-md border transition-colors ${
                activeCategory === c
                  ? 'bg-primary text-on-primary border-primary'
                  : 'bg-surface border-outline-variant text-on-surface-variant hover:bg-surface-container-highest'
              }`}
            >
              {c} ({c === 'All' ? (countsData?.total ?? 0) : categories[c]})
            </button>
          ))}
        </div>
        <input
          type="text"
          placeholder="Search subject / sender"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="px-3 py-2 rounded-lg border border-outline-variant text-body-md w-64"
        />
      </div>

      {error && <div className="text-body-md text-error">{error}</div>}

      <div className="flat-card overflow-hidden">
        <DataTable
          columns={columns}
          data={rows}
          keyField="id"
          page={page}
          pageSize={pageSize}
          total={total}
          onPageChange={setPage}
          loading={loading}
          loadingSkeleton={<LoadingSkeleton type="table" />}
          emptyState={<EmptyState message="No emails match this filter." />}
        />
      </div>
    </div>
  );
};

export default Categories;

export const Pagination = ({ total, page, pageSize, onPageChange }) => {
  const totalPages = Math.ceil(total / pageSize);
  
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-between px-6 py-3 bg-surface border-t border-outline-variant">
      <div className="text-body-md text-on-surface-variant">
        Showing <span className="font-medium">{(page - 1) * pageSize + 1}</span> to{' '}
        <span className="font-medium">{Math.min(page * pageSize, total)}</span> of{' '}
        <span className="font-medium">{total}</span> results
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
          className="px-3 py-1 border border-outline-variant rounded-md text-body-md text-on-surface disabled:opacity-50 disabled:cursor-not-allowed hover:bg-surface-container-highest transition-colors"
        >
          Previous
        </button>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page === totalPages}
          className="px-3 py-1 border border-outline-variant rounded-md text-body-md text-on-surface disabled:opacity-50 disabled:cursor-not-allowed hover:bg-surface-container-highest transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  );
};

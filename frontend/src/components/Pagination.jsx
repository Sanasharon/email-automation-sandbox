export const Pagination = ({ total, page, pageSize, onPageChange, onPageSizeChange }) => {
  const totalPages = Math.ceil(total / pageSize) || 1;
  
  if (total === 0) return null;

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between px-6 py-3 bg-surface border-t border-outline-variant gap-4">
      <div className="text-body-md text-on-surface-variant flex items-center gap-4">
        <div>
          Showing <span className="font-medium">{(page - 1) * pageSize + 1}</span>–
          <span className="font-medium">{Math.min(page * pageSize, total)}</span> of{' '}
          <span className="font-medium">{total}</span> emails
        </div>
        
        {onPageSizeChange && (
          <div className="flex items-center gap-2 border-l pl-4 border-outline-variant">
            <label htmlFor="pageSize" className="sr-only">Rows per page</label>
            <select 
              id="pageSize" 
              value={pageSize} 
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
              className="bg-transparent border border-outline-variant rounded-md text-body-md py-0.5 px-2 focus:ring-primary focus:border-primary"
            >
              {[10, 25, 50, 100].map(size => (
                <option key={size} value={size}>{size} / page</option>
              ))}
            </select>
          </div>
        )}
      </div>
      
      <div className="flex items-center gap-4">
        <span className="text-body-md text-on-surface-variant">
          Page <span className="font-medium">{page}</span> of {totalPages}
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page === 1}
            className="px-3 py-1 border border-outline-variant rounded-md text-body-md text-on-surface disabled:opacity-50 disabled:cursor-not-allowed hover:bg-surface-container-highest transition-colors"
          >
            ◀ Previous
          </button>
          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page === totalPages}
            className="px-3 py-1 border border-outline-variant rounded-md text-body-md text-on-surface disabled:opacity-50 disabled:cursor-not-allowed hover:bg-surface-container-highest transition-colors"
          >
            Next ▶
          </button>
        </div>
      </div>
    </div>
  );
};


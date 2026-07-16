export const LoadingSkeleton = ({ type = 'table', rows = 5 }) => {
  if (type === 'table') {
    return (
      <div className="w-full flex flex-col">
        <div className="h-10 bg-surface-container-highest animate-pulse mb-2 rounded"></div>
        {[...Array(rows)].map((_, i) => (
          <div key={i} className="h-14 bg-surface-container-low animate-pulse mb-1 border-b border-outline-variant/30"></div>
        ))}
      </div>
    );
  }

  if (type === 'card') {
    return (
      <div className="flat-card p-6 flex flex-col justify-between animate-pulse">
        <div className="h-4 bg-surface-container-highest rounded w-1/2 mb-4"></div>
        <div className="h-10 bg-surface-container-highest rounded w-1/3"></div>
      </div>
    );
  }

  return (
    <div className="w-full h-full min-h-[100px] bg-surface-container-low animate-pulse rounded"></div>
  );
};

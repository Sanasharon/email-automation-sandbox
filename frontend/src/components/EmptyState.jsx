export const EmptyState = ({ message, actionText, onAction, icon }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      <div className="w-12 h-12 rounded-full bg-surface-container-high flex items-center justify-center mb-4">
        {icon || <span className="material-symbols-outlined text-on-surface-variant text-[24px]">inbox</span>}
      </div>
      <p className="text-body-md text-on-surface-variant mb-4">{message}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="px-4 py-2 bg-primary text-on-primary rounded-md font-medium text-body-md hover:bg-primary/90 transition-colors"
        >
          {actionText}
        </button>
      )}
    </div>
  );
};

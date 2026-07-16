import { X } from 'lucide-react';

export const Modal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto overflow-x-hidden bg-black/50 p-4">
      <div className="relative w-full max-w-lg rounded-lg bg-surface shadow-lg border border-outline-variant">
        <div className="flex items-center justify-between p-4 border-b border-outline-variant">
          <h3 className="font-headline-sm text-on-surface">{title}</h3>
          <button
            onClick={onClose}
            className="text-on-surface-variant hover:text-on-surface hover:bg-surface-container-highest p-1 rounded-md transition-colors"
          >
            <X size={20} />
          </button>
        </div>
        <div className="p-4 max-h-[70vh] overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
};

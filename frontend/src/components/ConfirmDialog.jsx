import { Modal } from './Modal';

export const ConfirmDialog = ({ isOpen, onClose, onConfirm, title, message, confirmText = 'Confirm', cancelText = 'Cancel', isDestructive = false }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title}>
      <div className="flex flex-col gap-6">
        <p className="text-body-md text-on-surface-variant">{message}</p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-body-md font-medium text-on-surface-variant border border-outline-variant rounded-md hover:bg-surface-container-highest transition-colors"
          >
            {cancelText}
          </button>
          <button
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className={`px-4 py-2 text-body-md font-medium rounded-md transition-colors ${
              isDestructive 
                ? 'bg-error text-on-error hover:bg-error/90' 
                : 'bg-primary text-on-primary hover:bg-primary/90'
            }`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </Modal>
  );
};

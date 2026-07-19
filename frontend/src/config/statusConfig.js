export const statusConfig = {
  // Workflow Control
  running: { label: 'Running', bgColor: 'bg-[#DAFBE1]', textColor: 'text-[#1A7F37]', showRetry: false },
  active: { label: 'Active', bgColor: 'bg-[#DAFBE1]', textColor: 'text-[#1A7F37]', showRetry: false },
  paused: { label: 'Paused', bgColor: 'bg-surface-container-high', textColor: 'text-on-surface-variant', showRetry: false },
  disabled: { label: 'Disabled', bgColor: 'bg-surface-container-high', textColor: 'text-on-surface-variant', showRetry: false },
  
  // Email Monitoring & Automation Activity (Inbound - current)
  // Note: This module currently reflects inbound collection status only.
  // Outbound send-tracking (Sent/Delivered/Bounced) is a planned future capability 
  // and should extend this same config pattern, not replace it.
  collected: { label: 'Collected', bgColor: 'bg-surface-variant', textColor: 'text-on-surface-variant', showRetry: false },
  completed: { label: 'Completed', bgColor: 'bg-[#DAFBE1]', textColor: 'text-[#1A7F37]', showRetry: false },
  failed: { label: 'Failed', bgColor: 'bg-error-container', textColor: 'text-on-error-container', showRetry: true },

  // Outbound (future capability)
  sent: { label: 'Sent', bgColor: 'bg-[#DAFBE1]', textColor: 'text-[#1A7F37]', showRetry: false },
  delivered: { label: 'Delivered', bgColor: 'bg-[#DAFBE1]', textColor: 'text-[#1A7F37]', showRetry: false },
  bounced: { label: 'Bounced', bgColor: 'bg-error-container', textColor: 'text-on-error-container', showRetry: true },
  
  pending: { label: 'Pending', bgColor: 'bg-[#FFF8C5]', textColor: 'text-[#9A6700]', showRetry: false },
  queued: { label: 'Queued', bgColor: 'bg-[#FFF8C5]', textColor: 'text-[#9A6700]', showRetry: false },
  delayed: { label: 'Delayed', bgColor: 'bg-[#FFF8C5]', textColor: 'text-[#9A6700]', showRetry: false },
  error: { label: 'Error', bgColor: 'bg-error-container', textColor: 'text-on-error-container', showRetry: true },
  unknown: { label: 'Unknown', bgColor: 'bg-surface-variant', textColor: 'text-on-surface', showRetry: false },
  
  processing: { label: 'Processing', bgColor: 'bg-primary-container', textColor: 'text-on-primary-container', showRetry: false },
  success: { label: 'Success', bgColor: 'bg-[#DAFBE1]', textColor: 'text-[#1A7F37]', showRetry: false },
  info: { label: 'Info', bgColor: 'bg-secondary-container', textColor: 'text-on-secondary-container', showRetry: false }
};

export const getStatusConfig = (status) => {
  if (!status) return statusConfig.unknown;
  return statusConfig[status.toLowerCase()] || { label: status, bgColor: 'bg-surface-variant', textColor: 'text-on-surface', showRetry: false };
};

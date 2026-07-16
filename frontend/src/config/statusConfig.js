export const statusConfig = {
  // Workflow Control
  running: { label: 'Running', bgColor: 'bg-[#DAFBE1]', textColor: 'text-[#1A7F37]' },
  active: { label: 'Active', bgColor: 'bg-[#DAFBE1]', textColor: 'text-[#1A7F37]' },
  paused: { label: 'Paused', bgColor: 'bg-surface-container-high', textColor: 'text-on-surface-variant' },
  disabled: { label: 'Disabled', bgColor: 'bg-surface-container-high', textColor: 'text-on-surface-variant' },
  
  // Email Monitoring & Automation Activity
  sent: { label: 'Sent', bgColor: 'bg-[#DAFBE1]', textColor: 'text-[#1A7F37]' },
  delivered: { label: 'Delivered', bgColor: 'bg-[#DAFBE1]', textColor: 'text-[#1A7F37]' },
  pending: { label: 'Pending', bgColor: 'bg-[#FFF8C5]', textColor: 'text-[#9A6700]' },
  queued: { label: 'Queued', bgColor: 'bg-[#FFF8C5]', textColor: 'text-[#9A6700]' },
  delayed: { label: 'Delayed', bgColor: 'bg-[#FFF8C5]', textColor: 'text-[#9A6700]' },
  failed: { label: 'Failed', bgColor: 'bg-error-container', textColor: 'text-on-error-container' },
  bounced: { label: 'Bounced', bgColor: 'bg-error-container', textColor: 'text-on-error-container' },
  error: { label: 'Error', bgColor: 'bg-error-container', textColor: 'text-on-error-container' },
  
  processing: { label: 'Processing', bgColor: 'bg-primary-container', textColor: 'text-on-primary-container' },
  completed: { label: 'Completed', bgColor: 'bg-[#DAFBE1]', textColor: 'text-[#1A7F37]' },
  success: { label: 'Success', bgColor: 'bg-[#DAFBE1]', textColor: 'text-[#1A7F37]' },
  info: { label: 'Info', bgColor: 'bg-secondary-container', textColor: 'text-on-secondary-container' }
};

export const getStatusConfig = (status) => {
  return statusConfig[status?.toLowerCase()] || { label: status, bgColor: 'bg-surface-variant', textColor: 'text-on-surface' };
};

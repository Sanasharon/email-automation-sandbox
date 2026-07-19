export const normalizeEmail = (raw) => {
  if (!raw) return null;
  // ─── Field-name mapping (CONFIRMED against Sprint 2 /emails/ endpoint 2026-07-17) ───
  // raw.sender_email      → sender     (backend uses sender_email, explicitly for inbound)
  // raw.processing_status → status     (backend uses processing_status, not status)
  // raw.received_at       → sent_time  (backend uses received_at, not sent_at)
  // raw.subject           → subject    (✅ confirmed match)
  // raw.id                → id         (✅ confirmed match)
  // raw.last_processing_error → error_message (guessed, not yet confirmed)
    // raw.labels[0]         → removed: frontend will no longer guess category from labels
    return {
      id: raw.id,
      sender: raw.sender_email || raw.sender || 'Unknown Sender',
      subject: raw.subject || '(No Subject)',
      category: raw.retention_category || raw.category || 'Uncategorized',
      labels: raw.labels || [],
    status: (() => {
      const s = raw.processing_status || raw.email_status || raw.status || 'unknown';
      return s === 'parsed' ? 'completed' : s;
    })(),
    sent_time: raw.received_at || raw.sent_at || new Date().toISOString(),
    error_message: (raw.last_processing_error === '' ? null : raw.last_processing_error) || null,
    retry_count: raw.retry_count || 0,
    provider_message_id: raw.provider_message_id || null,
    provider_thread_id: raw.provider_thread_id || null,
    workflow_execution_id: raw.workflow_execution_id || 'unknown',
    
    // Workflow tracking
    workflow_name: raw.workflow_name || 'Not Processed',
    last_action: raw.last_action || 'Skipped',
    workflow_status: raw.workflow_status || null,
    processing_duration: raw.processing_duration || 0,
    has_attachments: raw.has_attachments || false,
    
    // Details
    to_recipients: raw.to_recipients || [],
    cc_recipients: raw.cc_recipients || [],
    bcc_recipients: raw.bcc_recipients || [],
    body_text: raw.body_text || null,
    body_html: raw.body_html || null,
    attachments: raw.attachments || [],
    execution_timeline: raw.execution_timeline || []
  };
};

export const normalizeWorkflowExecution = (raw) => {
  if (!raw) return null;
  return {
    id: raw.id,
    task_id: raw.id, // For queue
    task_name: raw.current_step || 'Execution Step',
    status: raw.status || 'unknown',
    timestamp: raw.completed_at || raw.started_at || new Date().toISOString(),
    type: 'workflow_execution',
    title: raw.workflow_id ? `Workflow Execution: ${raw.workflow_id}` : 'Unknown Workflow',
    description: `Step: ${raw.current_step || 'N/A'}`,
    estimated_time: '1m' // Fallback if backend doesn't provide
  };
};

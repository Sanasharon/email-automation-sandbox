const axios = require('axios');

const normalizeEmail = (raw) => {
  if (!raw) return null;
  return {
    id: raw.id,
    recipient: raw.sender_email || raw.recipient || 'Unknown Sender',
    subject: raw.subject || '(No Subject)',
    category: (() => {
      if (raw.labels && Array.isArray(raw.labels)) {
        const customLabels = raw.labels.filter(l => !['UNREAD', 'IMPORTANT', 'SENT', 'INBOX', 'STARRED', 'TRASH', 'SPAM'].includes(l));
        if (customLabels.length > 0) return customLabels[0];
      }
      return raw.category || 'Uncategorized';
    })(),
    status: raw.processing_status || raw.email_status || raw.status || 'unknown',
    sent_time: raw.received_at || raw.sent_at || new Date().toISOString(),
    error_message: (raw.last_processing_error === '' ? null : raw.last_processing_error) || null,
    retry_count: raw.retry_count || 0,
    workflow_execution_id: raw.workflow_execution_id || 'unknown'
  };
};

const getWorkflows = (rawData) => {
  return rawData.map(w => {
    let category = "";
    if (w.trigger_conditions_json?.rules?.length > 0) {
       category = w.trigger_conditions_json.rules[0].value;
       if (category === 'any') category = '';
    }
    let team = "";
    if (w.description && w.description.startsWith("Target Team: ")) {
       team = w.description.replace("Target Team: ", "");
    }
    return {
      ...w,
      status: w.is_active ? 'active' : 'disabled',
      trigger_type: 'webhook',
      last_run: w.updated_at,
      category_filter: category,
      destination_team: team
    };
  });
};

(async () => {
  try {
    const emailRes = await axios.get('http://localhost:8000/emails/?limit=1');
    const emails = Array.isArray(emailRes.data) ? emailRes.data : emailRes.data.data;
    console.log("=== NORMALIZED EMAIL ===");
    console.log(JSON.stringify(normalizeEmail(emails[0]), null, 2));

    const wfRes = await axios.get('http://localhost:8000/api/v1/workflows');
    const workflows = Array.isArray(wfRes.data.data) ? wfRes.data.data : [];
    console.log("\n=== NORMALIZED WORKFLOW ===");
    console.log(JSON.stringify(getWorkflows(workflows)[0], null, 2));

  } catch (e) {
    console.error(e);
  }
})();

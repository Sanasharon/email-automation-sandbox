import axios from 'axios';
import { USE_MOCK_DATA } from '../config/appConfig';
import { normalizeEmail, normalizeWorkflowExecution } from './adapters';

const delay = (ms) => new Promise(res => setTimeout(res, ms));

const validateArray = (data, name) => {
  if (!Array.isArray(data)) throw new Error(`Unable to load data: Unexpected response format for ${name}`);
  return data;
};

const validateObject = (data, name) => {
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error(`Unable to load data: Unexpected response format for ${name}`);
  return data;
};
// Create Axios client using environment variable or default to localhost
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const axiosClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Intercept responses to unwrap the `APIResponse` generic structure
axiosClient.interceptors.response.use(
  (response) => {
    const resData = response.data;
    // FastAPI success_response format: { success: true, data: { ... } }
    if (resData && resData.success !== undefined) {
       return resData.data; 
    }
    return resData;
  },
  (error) => {
    console.error("API Error:", error);
    return Promise.reject(error);
  }
);

export const api = {
  // ---------------------------------------------------------
  // Dashboard
  // ---------------------------------------------------------
  getDashboardSummary: async () => {
    const response = await axiosClient.get('/dashboard/summary');
    return validateObject(response, 'Dashboard Summary');
  },
  
  getRecentActivity: async () => {
    const response = await axiosClient.get('/dashboard/recent-activity');
    return validateArray(response.data || response, 'Recent Activity');
  },

  // ---------------------------------------------------------
  // Workflows
  // ---------------------------------------------------------
  getCategories: async () => {
    const response = await axiosClient.get('/workflows/categories');
    const data = validateArray(response.data || response, 'Categories');
    return { data }; // Wrap array for UI dropdowns
  },

  getWorkflows: async ({ status = 'all', search = '', page = 1, pageSize = 10 }) => {
    const response = await axiosClient.get('/workflows', {
      params: { search, page, page_size: pageSize }
    });
    
    const rawData = validateArray(response.data || response, 'Workflows');
    
    // Map backend response -> UI Expected Format
    const mappedData = rawData.map(w => {
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
        trigger_type: 'webhook', // Fallback for UI visualization
        last_run: w.updated_at,
        category_filter: category,
        destination_team: team
      };
    });
    
    return {
      data: mappedData,
      total: response.meta?.total_items || 0,
      page: response.meta?.current_page || page,
      page_size: response.meta?.page_size || pageSize
    };
  },
  
  createWorkflow: async (workflow) => {
    // Fetch a valid mailbox_account_id from an existing workflow
    const existing = await api.getWorkflows({ pageSize: 1 });
    let mailboxId = "00000000-0000-0000-0000-000000000000";
    if (existing && existing.data && existing.data.length > 0) {
      mailboxId = existing.data[0].mailbox_account_id;
    } else {
      // Fallback to the known UUID from our test db
      mailboxId = "276681d7-7ca4-47aa-851b-fd046ffc1ef4"; 
    }
    
    // Map UI form fields -> Backend schema fields
    const payload = {
      name: workflow.name || "Untitled Workflow",
      description: workflow.description || "No description",
      mailbox_account_id: mailboxId,
      trigger_conditions_json: workflow.trigger_conditions_json || { operator: "AND", rules: [] },
      actions_json: workflow.actions_json || { actions: [] },
      is_active: false
    };

    return await axiosClient.post('/workflows', payload);
  },
  
  updateWorkflow: async (id, workflow) => {
    const payload = {
      name: workflow.name,
      description: workflow.description,
      trigger_conditions_json: workflow.trigger_conditions_json,
      actions_json: workflow.actions_json
    };
    return await axiosClient.put(`/workflows/${id}`, payload);
  },
  
  deleteWorkflow: async (id) => {
    await axiosClient.delete(`/workflows/${id}`);
    return { success: true };
  },
  
  getWorkflowExecutions: async (id) => {
    const response = await axiosClient.get(`/workflows/${id}/executions`);
    return response || [];
  },
  
  toggleWorkflowState: async (id, action) => {
    let apiAction = action;
    if (action === 'start') apiAction = 'enable';
    if (action === 'stop') apiAction = 'disable';
    
    const updated = await axiosClient.patch(`/workflows/${id}/state`, { action: apiAction });
    return {
      ...updated,
      status: updated.is_active ? 'active' : 'disabled',
      trigger_type: 'webhook',
      last_run: updated.updated_at
    };
  },

  // ---------------------------------------------------------
  // Emails
  // TODO [BACKEND STANDARDIZATION]: This endpoint uses the Sprint 2 legacy route /emails/
  // and does NOT follow the /api/v1/ convention used by the rest of the API (workflows, dashboard).
  // The real call goes to the axiosClient baseURL's HOST:PORT + /emails/ directly (not /api/v1/emails).
  // Ask the backend team to either:
  //   (a) add a /api/v1/emails route that wraps/replaces this one, OR
  //   (b) keep it at /emails/ and document it as a deliberate exception.
  // Until then, this call uses a separate Axios instance without the /api/v1 prefix.
  // ---------------------------------------------------------
  getEmails: async ({ status = 'all', search = '', page = 1, pageSize = 10 }) => {
    if (USE_MOCK_DATA) {
      const mockRawData = [
          { id: '1', sender: 'test@example.com', subject: 'Invoice Mock', category: 'finance', status: 'sent', sent_time: new Date().toISOString() },
          { id: '2', sender: 'user@domain.com', subject: 'Welcome Mock', category: 'onboarding', status: 'failed', sent_time: new Date().toISOString() }
      ];
      return { 
        data: mockRawData.map(normalizeEmail), 
        total: 2, page, page_size: pageSize 
      };
    }
    try {
      const baseHost = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace('/api/v1', '');
      const response = await axios.get(`${baseHost}/emails/`, { params: { status, search, skip: (page - 1) * pageSize, limit: pageSize } });
      const responseData = response.data || response;
      const rawData = validateArray(responseData.data, 'Emails');
      const normalizedData = rawData.map(normalizeEmail);
      return { data: normalizedData, total: responseData.total || rawData.length, page, page_size: pageSize };
    } catch (e) {
      console.error('Failed to fetch emails:', e);
      throw e;
    }
  },

  getEmailDetail: async (id) => {
    if (USE_MOCK_DATA) {
      return normalizeEmail({ id, subject: 'Mock Details', sender_email: 'mock@mock.com', body_text: 'Mock content', execution_timeline: [] });
    }
    const baseHost = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace('/api/v1', '');
    const response = await axios.get(`${baseHost}/emails/${id}`);
    const responseData = response.data || response;
    return normalizeEmail(responseData.data || responseData);
  },
  
  retryEmail: async (id) => {
    if (USE_MOCK_DATA) {
      return { id, status: 'pending', sent_time: new Date().toISOString() };
    }
    const response = await axiosClient.post(`/emails/${id}/retry`);
    return normalizeEmail(validateObject(response.data || response, 'Email Retry Response'));
  },

  getEmailStats: async () => {
    if (USE_MOCK_DATA) {
      return { total: 100, collected: 80, parsed: 10, completed: 5, failed: 5 };
    }
    const baseHost = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace('/api/v1', '');
    const response = await axios.get(`${baseHost}/emails/stats`);
    return response.data || response;
  },

  exportEmails: async (status = 'all', search = '') => {
    if (USE_MOCK_DATA) {
      return; // Mock doesn't support real file download
    }
    const baseHost = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace('/api/v1', '');
    const response = await axios.get(`${baseHost}/emails/export`, {
      params: { status, search },
      responseType: 'blob'
    });
    
    // Extract filename from headers or default
    const contentDisposition = response.headers['content-disposition'];
    let filename = `email-monitoring-export-${new Date().toISOString().split('T')[0]}.xlsx`;
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^"]+)"?/);
      if (match && match[1]) filename = match[1];
    }
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  // ---------------------------------------------------------
  // Automation Activity / Operations Dashboard
  // ---------------------------------------------------------
  getOperationsSummary: async () => {
    const baseHost = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace('/api/v1', '');
    const response = await axios.get(`${baseHost}/dashboard/summary`);
    return response.data || {};
  },
  
  getRecentActivity: async () => {
    const response = await axiosClient.get('/dashboard/recent-activity');
    return response || { data: [] };
  },

  getRecentSyncs: async () => {
    const baseHost = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace('/api/v1', '');
    const response = await axios.get(`${baseHost}/dashboard/recent-syncs?limit=5`);
    return response.data;
  },

  getMailboxes: async () => {
    const baseHost = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace('/api/v1', '');
    const response = await axios.get(`${baseHost}/dashboard/mailboxes`);
    return response.data;
  },

  getCurrentTask: async () => {
    if (USE_MOCK_DATA) {
      return {
        task_id: "mock-1",
        task_name: "Mock Sync Task",
        description: "Syncing mock emails...",
        progress: 45,
        eta_seconds: 12,
        worker_id: "worker-1"
      };
    }
    try {
      // Axios interceptor unwraps APIResponse -> data = CurrentTaskResponse { current_task: {...} | null }
      const response = await axiosClient.get('/automation/current-task');
      return response?.current_task || null;
    } catch (e) {
      console.error('Failed to fetch current task:', e);
      throw e;
    }
  },
  
  getAutomationQueue: async () => { 
    if (USE_MOCK_DATA) {
      return { data: [{ task_id: 'q-1', task_name: 'Process rules', status: 'queued', estimated_time: '2m' }] };
    }
    try {
      // Axios interceptor unwraps APIResponse -> data = QueueResponse { data: [...], total: n }
      const response = await axiosClient.get('/automation/queue');
      const rawData = validateArray(response?.data || [], 'Automation Queue');
      return { data: rawData, total: response?.total || rawData.length };
    } catch (e) {
      console.error('Failed to fetch automation queue:', e);
      throw e;
    }
  },
  
  getAutomationHistory: async () => { 
    if (USE_MOCK_DATA) {
      return { 
        data: [
          { id: 'h-1', status: 'success', type: 'workflow_success', title: 'Workflow Executed', description: 'Step completed', timestamp: new Date().toISOString() }
        ] 
      };
    }
    try {
      // Axios interceptor unwraps APIResponse -> data = HistoryResponse { data: [...], total, page, page_size }
      const response = await axiosClient.get('/automation/history');
      const rawData = validateArray(response?.data || [], 'Automation History');
      return { data: rawData.map(normalizeWorkflowExecution), total: response?.total || 0 };
    } catch (e) {
      console.error('Failed to fetch automation history:', e);
      throw e;
    }
  },

  // ---------------------------------------------------------
  // Notifications
  // ---------------------------------------------------------
  getNotifications: async () => {
    if (USE_MOCK_DATA) {
      return [
        { id: '1', type: 'error', message: 'Workflow "Finance" failed on email "Invoice"', timestamp: new Date().toISOString() },
        { id: '2', type: 'success', message: 'Workflow "Onboarding" matched a new email', timestamp: new Date(Date.now() - 3600000).toISOString() }
      ];
    }
    const response = await axiosClient.get('/notifications');
    return response || [];
  }
};

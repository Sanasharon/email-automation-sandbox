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

// Intercept requests to attach auth token
axiosClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercept responses to unwrap the `APIResponse` generic structure
axiosClient.interceptors.response.use(
  (response) => {
    const resData = response.data;
    // Some endpoints return { success, data }, others return { success, message } or raw arrays/objects
    if (resData && resData.success !== undefined && resData.data !== undefined) {
       return resData.data;
    }
    // Return whatever we got — never undefined
    return resData;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    } else if (error.response?.status === 403) {
      console.warn('Permission denied:', error.config?.url);
    } else if (!error.response) {
      console.error("Network Failure: Backend is unreachable.", error);
    } else if (error.response?.status >= 500) {
      console.error("Server Error:", error.config?.url, error.response?.status);
    }
    return Promise.reject(error);
  }
);

// Add global interceptors for raw axios calls as well
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    } else if (!error.response) {
      console.error("Network Failure: Backend is unreachable.");
      // Could dispatch a global event here for a toast notification
    } else if (error.response?.status >= 500) {
      console.error("Server Error: Something went wrong on the backend.");
    }
    return Promise.reject(error);
  }
);

export const api = {
  // ---------------------------------------------------------
  // Auth
  // ---------------------------------------------------------
  login: async (credentials) => {
    // credentials: { email, password }
    const response = await axiosClient.post('/auth/login', credentials);
    return response; // { success, token, user }
  },

  getCurrentUser: async () => {
    const response = await axiosClient.get('/auth/me');
    return response?.user ?? response;
  },

  
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

  getAnalyticsSummary: async (days = 7) => {
    const response = await axiosClient.get('/analytics/summary', { params: { days } });
    return validateObject(response, 'Analytics Summary');
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
    try {
      const response = await axiosClient.get('/workflows', {
        params: { search, page, page_size: pageSize }
      });
      
      const rawData = Array.isArray(response.data) ? response.data : (Array.isArray(response) ? response : []);
      
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
        total: response.meta?.total_items || mappedData.length,
        page: response.meta?.current_page || page,
        page_size: response.meta?.page_size || pageSize
      };
    } catch (e) {
      console.error('Failed to fetch workflows:', e);
      return { data: [], total: 0, page, page_size: pageSize };
    }
  },
  
  createWorkflow: async (workflow) => {
    let mailboxId = workflow.mailbox_account_id;
    if (!mailboxId) {
      const mailboxes = await api.getMailboxes();
      if (mailboxes && mailboxes.length > 0) {
        mailboxId = mailboxes[0].id;
      }
    }
    if (!mailboxId) {
      throw new Error("No connected Gmail account found. Please connect your Gmail account in Settings before creating workflows.");
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
      const response = await axios.get(`${baseHost}/emails/`, { 
        params: { status, search, skip: (page - 1) * pageSize, limit: pageSize },
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      const responseData = response.data || response;
      const rawData = Array.isArray(responseData.data) ? responseData.data : (Array.isArray(responseData) ? responseData : []);
      const normalizedData = rawData.map(normalizeEmail);
      return { data: normalizedData, total: responseData.total || rawData.length, page, page_size: pageSize };
    } catch (e) {
      console.error('Failed to fetch emails:', e);
      return { data: [], total: 0, page, page_size: pageSize };
    }
  },

  getEmailDetail: async (id) => {
    if (USE_MOCK_DATA) {
      return normalizeEmail({ id, subject: 'Mock Details', sender_email: 'mock@mock.com', body_text: 'Mock content', execution_timeline: [] });
    }
    const baseHost = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace('/api/v1', '');
    const response = await axios.get(`${baseHost}/emails/${id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    });
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
    const response = await axios.get(`${baseHost}/emails/stats`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    });
    return response.data || response;
  },

  exportEmails: async (status = 'all', search = '') => {
    if (USE_MOCK_DATA) {
      return; // Mock doesn't support real file download
    }
    const baseHost = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace('/api/v1', '');
    const response = await axios.get(`${baseHost}/emails/export`, {
      params: { status, search },
      responseType: 'blob',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
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
  
  getRecentSyncs: async () => {
    const baseHost = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace('/api/v1', '');
    const response = await axios.get(`${baseHost}/dashboard/recent-syncs?limit=5`);
    return response.data;
  },

   // Replace the getMailboxes function with this:
getMailboxes: async () => {
  try {
    // Primary attempt using axiosClient (will call `${VITE_API_BASE_URL}/mailboxes`)
    const resp = await axiosClient.get('/mailboxes');
    return resp;
  } catch (err) {
    // If the configured path returned 404, try host-root fallback (no /api/v1)
    if (err?.response?.status === 404) {
      try {
        const configured = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
        const hostRoot = configured.replace(/\/api\/v1\/?$/, '').replace(/\/$/, '');
        const url = `${hostRoot}/mailboxes/`;
        const r2 = await axios.get(url, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        return r2.data || r2;
      } catch (err2) {
        console.error('Fallback getMailboxes failed', err2);
        throw err; // rethrow original for debugging
      }
    }
    throw err;
  }
},

  getMailboxStatus: async () => {
    const response = await axiosClient.get('/mailboxes/status');
    return response.data || response;
  },

  connectMailbox: async () => {
    const response = await axiosClient.post('/mailboxes/connect');
    return response.data || response;
  },

  syncMailbox: async (mailboxId) => {
    const response = await axiosClient.post(`/mailboxes/${mailboxId}/sync`);
    return response.data || response;
  },

  disconnectMailbox: async (mailboxId, deleteData = false) => {
    const response = await axiosClient.post(`/mailboxes/${mailboxId}/disconnect?delete_data=${deleteData}`);
    return response.data || response;
  },

  reconnectMailbox: async (mailboxId) => {
    const response = await axiosClient.post(`/mailboxes/${mailboxId}/reconnect`);
    return response.data || response;
  },

  switchMailboxAccount: async () => {
    const response = await axiosClient.post('/mailboxes/switch-account');
    return response.data || response;
  },

  getSystemStatus: async () => {
    const response = await axiosClient.get('/system/status');
    return response || {};
  },

  // These three were called by the Monitoring page but never defined here —
  // that's why Queue Activity / Processing Logs / Recent Errors always
  // showed placeholder dashes regardless of real backend state.
  getQueueStatus: async () => {
    const response = await axiosClient.get('/system/queue');
    return response || {};
  },

  getProcessingLogs: async (limit = 20) => {
    const response = await axiosClient.get('/system/logs', { params: { limit } });
    return response?.logs || [];
  },

  getRecentErrors: async (limit = 20) => {
    const response = await axiosClient.get('/system/errors', { params: { limit } });
    return response?.errors || [];
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
  },

  // ---------------------------------------------------------
  // Sprint 5: Prompt Templates & AI Approvals
  // ---------------------------------------------------------
  getPromptTemplates: async () => {
    try {
      const response = await axiosClient.get('/prompt-templates');
      return response || [];
    } catch (e) {
      console.error('Failed to fetch prompt templates:', e);
      return [];
    }
  },

  createPromptTemplate: async (payload) => {
    try {
      const response = await axiosClient.post('/prompt-templates', payload);
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  deletePromptTemplate: async (id) => {
    try {
      const response = await axiosClient.delete(`/prompt-templates/${id}`);
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  updatePromptTemplate: async (id, payload) => {
    try {
      const response = await axiosClient.put(`/prompt-templates/${id}`, payload);
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  testPromptTemplate: async (id, sampleInputs) => {
    try {
      const response = await axiosClient.post(`/prompt-templates/${id}/test`, { sample_inputs: sampleInputs });
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  validatePromptTemplate: async (id) => {
    try {
      const response = await axiosClient.get(`/prompt-templates/${id}/validate`);
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  // ---------------------------------------------------------
  // AI Providers
  // ---------------------------------------------------------
  getAIProviders: async () => {
    try {
      const response = await axiosClient.get('/ai-providers');
      return response || [];
    } catch (e) {
      console.error('Failed to fetch AI providers:', e);
      return [];
    }
  },

  createAIProvider: async (payload) => {
    try {
      const response = await axiosClient.post('/ai-providers', payload);
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  updateAIProvider: async (id, payload) => {
    try {
      const response = await axiosClient.put(`/ai-providers/${id}`, payload);
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  deleteAIProvider: async (id) => {
    try {
      const response = await axiosClient.delete(`/ai-providers/${id}`);
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  testAIProvider: async (id) => {
    try {
      const response = await axiosClient.post(`/ai-providers/${id}/test`);
      return response || { success: false, error: 'No response from server' };
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Test failed';
      return { success: false, error: msg };
    }
  },

  // ---------------------------------------------------------
  // Email Templates
  // ---------------------------------------------------------
  getEmailTemplates: async () => {
    try {
      const response = await axiosClient.get('/email-templates');
      return response || [];
    } catch (e) {
      console.error('Failed to fetch email templates:', e);
      return [];
    }
  },

  createEmailTemplate: async (payload) => {
    try {
      const response = await axiosClient.post('/email-templates', payload);
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  updateEmailTemplate: async (id, payload) => {
    try {
      const response = await axiosClient.put(`/email-templates/${id}`, payload);
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  deleteEmailTemplate: async (id) => {
    try {
      const response = await axiosClient.delete(`/email-templates/${id}`);
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  // ---------------------------------------------------------
  // System Logs
  // ---------------------------------------------------------
  getSystemLogs: async (params = {}) => {
    try {
      const queryParams = new URLSearchParams();
      if (params.level) queryParams.append('level', params.level);
      if (params.category) queryParams.append('category', params.category);
      if (params.page) queryParams.append('page', params.page);
      if (params.page_size) queryParams.append('page_size', params.page_size);
      const response = await axiosClient.get(`/logs?${queryParams.toString()}`);
      return response || [];
    } catch (e) {
      console.error('Failed to fetch system logs:', e);
      return [];
    }
  },

  getPendingApprovals: async () => {
    try {
      const response = await axiosClient.get('/ai-approvals');
      return response || [];
    } catch (e) {
      console.error('Failed to fetch AI pending approvals:', e);
      return [];
    }
  },

  approveAIDraft: async (id, editedText) => {
    try {
      const response = await axiosClient.post(`/ai-approvals/${id}/approve`, null, { params: { edited_text: editedText } });
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  rejectAIDraft: async (id) => {
    try {
      const response = await axiosClient.post(`/ai-approvals/${id}/reject`);
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  // --- Users Management ---
  getUsers: async (params = {}) => {
    try {
      const response = await axiosClient.get('/users', { params });
      return response || { data: [], meta: {} };
    } catch (e) {
      console.error('Failed to fetch users:', e);
      return { data: [], meta: {} };
    }
  },
  createUser: async (payload) => {
    try {
      const response = await axiosClient.post('/users', payload);
      return response || {};
    } catch (e) {
      throw e;
    }
  },
  updateUser: async (id, payload) => {
    try {
      const response = await axiosClient.put(`/users/${id}`, payload);
      return response || {};
    } catch (e) {
      throw e;
    }
  },
  deleteUser: async (id) => {
    try {
      const response = await axiosClient.delete(`/users/${id}`);
      return response || {};
    } catch (e) {
      throw e;
    }
  },

  // --- Roles Management ---
  getRoles: async (params = {}) => {
    try {
      const response = await axiosClient.get('/admin/roles', { params });
      return response || { data: [], meta: {} };
    } catch (e) {
      console.error('Failed to fetch roles:', e);
      return { data: [], meta: {} };
    }
  },
  createRole: async (payload) => {
    try {
      const response = await axiosClient.post('/admin/roles', payload);
      return response || {};
    } catch (e) {
      throw e;
    }
  },
  updateRole: async (id, payload) => {
    try {
      const response = await axiosClient.put(`/admin/roles/${id}`, payload);
      return response || {};
    } catch (e) {
      throw e;
    }
  },
  deleteRole: async (id) => {
    try {
      const response = await axiosClient.delete(`/admin/roles/${id}`);
      return response || {};
    } catch (e) {
      throw e;
    }
  },
};
export { axiosClient };
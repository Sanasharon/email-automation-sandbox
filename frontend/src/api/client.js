// Mock delay to simulate network
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Mock Data
let workflows = [
  {
    id: "wf_98231",
    name: "Data Ingestion Pipeline v4",
    status: "running",
    trigger_type: "cron",
    schedule: "*/10 * * * *",
    last_run: "2026-07-16T09:50:00Z",
    category_filter: "Billing Complaint",
    destination_team: "Finance"
  },
  {
    id: "wf_98232",
    name: "Support Ticket Router",
    status: "active",
    trigger_type: "webhook",
    schedule: null,
    last_run: "2026-07-16T10:15:00Z",
    category_filter: "Technical Support Request",
    destination_team: "Engineering"
  }
];

let emails = [
  {
    id: "em_10234",
    recipient: "marcus.kane@enterprise.io",
    subject: "Critical System Alert: Node Failure in Cluster-A7",
    category: "Server Downtime Alert",
    status: "failed",
    sent_time: "2026-07-16T09:42:11Z",
    retry_count: 1
  },
  {
    id: "em_10235",
    recipient: "alex.chen@startup.com",
    subject: "RE: Refund request for order #8812",
    category: "Refund Request",
    status: "sent",
    sent_time: "2026-07-16T10:05:00Z",
    retry_count: 0
  },
  {
    id: "em_10236",
    recipient: "sara.connor@sky.net",
    subject: "Welcome to Utservio Enterprise",
    category: "Account Access Issue",
    status: "delivered",
    sent_time: "2026-07-16T10:10:00Z",
    retry_count: 0
  },
  {
    id: "em_10237",
    recipient: "john.doe@invalid-domain.com",
    subject: "Your Weekly Digest",
    category: "Spam / Irrelevant",
    status: "bounced",
    sent_time: "2026-07-16T10:12:00Z",
    retry_count: 0
  },
  {
    id: "em_10238",
    recipient: "support@vendor.com",
    subject: "Invoice #9921 Processing",
    category: "Vendor Invoice",
    status: "pending",
    sent_time: "2026-07-16T10:20:00Z",
    retry_count: 0
  },
  {
    id: "em_10239",
    recipient: "it-admin@enterprise.io",
    subject: "Access Request Approved",
    category: "Access Request (Internal)",
    status: "failed",
    sent_time: "2026-07-16T10:25:00Z",
    retry_count: 2
  },
  {
    id: "em_10240",
    recipient: "finance-team@enterprise.io",
    subject: "Budget Approval Required for Q3",
    category: "Budget Approval Request",
    status: "delivered",
    sent_time: "2026-07-16T10:30:00Z",
    retry_count: 0
  }
];

const categories = [
  { category: "Billing Complaint", type: "Customer", department: "Finance", priority: "High" },
  { category: "Refund Request", type: "Customer", department: "Finance", priority: "Medium" },
  { category: "Product Inquiry", type: "Customer", department: "Sales", priority: "Low" },
  { category: "Technical Support Request", type: "Customer", department: "Engineering", priority: "High" },
  { category: "Account Access Issue", type: "Customer", department: "Support", priority: "High" },
  { category: "Subscription Cancellation", type: "Customer", department: "Retention", priority: "Medium" },
  { category: "Order Status Inquiry", type: "Customer", department: "Operations", priority: "Low" },
  { category: "Delivery Complaint", type: "Customer", department: "Operations", priority: "High" },
  { category: "Positive Feedback", type: "Customer", department: "Marketing", priority: "Low" },
  { category: "Partnership Inquiry", type: "Customer", department: "Business Dev", priority: "Medium" },
  { category: "Legal / Compliance Concern", type: "Customer", department: "Legal", priority: "Critical" },
  { category: "Spam / Irrelevant", type: "Customer", department: "—", priority: "Low" },
  
  { category: "Server Downtime Alert", type: "Internal", department: "Engineering", priority: "Critical" },
  { category: "Internal Policy Update", type: "Internal", department: "HR", priority: "Low" },
  { category: "Access Request (Internal)", type: "Internal", department: "IT", priority: "Medium" },
  { category: "System Backup Notification", type: "Internal", department: "Engineering", priority: "Low" },
  { category: "Budget Approval Request", type: "Internal", department: "Finance", priority: "Medium" },
  { category: "Employee Onboarding", type: "Internal", department: "HR", priority: "Medium" },
  { category: "Security Incident Report", type: "Internal", department: "Security", priority: "Critical" },
  { category: "Vendor Invoice", type: "Internal", department: "Finance", priority: "Medium" },
  { category: "Internal Escalation", type: "Internal", department: "Varies", priority: "High" },
  { category: "Meeting / Scheduling", type: "Internal", department: "—", priority: "Low" }
];

export const api = {
  // Dashboard
  getDashboardSummary: async () => {
    await delay(500);
    return {
      total_workflows: 1284,
      active_workflows: 842,
      emails_processed: 45200,
      successful_executions: 44150,
      failed_executions: 12,
      pending_jobs: 156,
      system_health_percent: 99.9,
      email_volume_series: [
        { time: "08:00", incoming: 120, automated: 95 },
        { time: "10:00", incoming: 180, automated: 150 },
        { time: "12:00", incoming: 220, automated: 190 },
        { time: "14:00", incoming: 300, automated: 280 },
        { time: "16:00", incoming: 250, automated: 220 },
        { time: "18:00", incoming: 150, automated: 140 },
        { time: "20:00", incoming: 90, automated: 85 }
      ]
    };
  },
  
  getRecentActivity: async () => {
    await delay(500);
    return {
      data: [
        {
          id: "act_001",
          type: "workflow_success",
          title: "Workflow \"Invoice_Parser_v2\" executed successfully",
          description: "Processed 14 internal attachments from AP@enterprise.com",
          timestamp: new Date(Date.now() - 2 * 60000).toISOString(),
          status: "success"
        },
        {
          id: "act_002",
          type: "email_error",
          title: "Email ingestion failed for \"Support_Ticket_Router\"",
          description: "Authentication timeout on IMAP relay 04",
          timestamp: new Date(Date.now() - 14 * 60000).toISOString(),
          status: "error"
        },
        {
          id: "act_003",
          type: "system_info",
          title: "System backup completed",
          description: "Snapshot #8841-B stored in primary cloud vault",
          timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
          status: "info"
        },
        {
          id: "act_004",
          type: "workflow_created",
          title: "New Workflow Created: \"Onboarding_Flow_v1\"",
          description: "Trigger: New User signup event (Webhook)",
          timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
          status: "success"
        }
      ]
    };
  },

  // Categories
  getCategories: async () => {
    await delay(300);
    return { data: categories };
  },

  // Workflows
  getWorkflows: async ({ status = 'all', search = '', page = 1, pageSize = 10 }) => {
    await delay(600);
    if (window.__FORCE_ERROR__) throw new Error('Mock API Connection Failed');
    
    let filtered = workflows;
    
    if (status !== 'all') {
      filtered = filtered.filter(w => w.status === status);
    }
    
    if (search) {
      filtered = filtered.filter(w => w.name.toLowerCase().includes(search.toLowerCase()));
    }
    
    const start = (page - 1) * pageSize;
    const paginated = filtered.slice(start, start + pageSize);
    
    return {
      data: paginated,
      total: filtered.length,
      page,
      page_size: pageSize
    };
  },
  
  createWorkflow: async (workflow) => {
    await delay(800);
    const newWf = {
      ...workflow,
      id: `wf_${Math.floor(Math.random() * 100000)}`,
      status: 'disabled',
      last_run: null
    };
    workflows = [newWf, ...workflows];
    return newWf;
  },
  
  updateWorkflow: async (id, updates) => {
    await delay(800);
    workflows = workflows.map(w => w.id === id ? { ...w, ...updates } : w);
    return workflows.find(w => w.id === id);
  },
  
  deleteWorkflow: async (id) => {
    await delay(800);
    workflows = workflows.filter(w => w.id !== id);
    return { success: true };
  },
  
  toggleWorkflowState: async (id, action) => {
    await delay(600);
    let newStatus = action;
    if (action === 'start') newStatus = 'running';
    if (action === 'stop') newStatus = 'paused';
    if (action === 'enable') newStatus = 'active';
    if (action === 'disable') newStatus = 'disabled';
    
    workflows = workflows.map(w => w.id === id ? { ...w, status: newStatus } : w);
    return workflows.find(w => w.id === id);
  },

  // Emails
  getEmails: async ({ status = 'all', search = '', page = 1, pageSize = 10 }) => {
    await delay(600);
    let filtered = emails;
    
    if (status !== 'all') {
      filtered = filtered.filter(e => e.status === status);
    }
    
    if (search) {
      const s = search.toLowerCase();
      filtered = filtered.filter(e => e.recipient.toLowerCase().includes(s) || e.subject.toLowerCase().includes(s));
    }
    
    const start = (page - 1) * pageSize;
    const paginated = filtered.slice(start, start + pageSize);
    
    return {
      data: paginated,
      total: filtered.length,
      page,
      page_size: pageSize
    };
  },
  
  retryEmail: async (id) => {
    await delay(800);
    emails = emails.map(e => {
      if (e.id === id) {
        return { ...e, status: 'pending', retry_count: (e.retry_count || 0) + 1 };
      }
      return e;
    });
    return emails.find(e => e.id === id);
  },

  // Automation
  getCurrentTask: async () => {
    await delay(400);
    return {
      task_id: "task_889",
      task_name: "Invoice-Parsing-Cluster-B7",
      description: "Advanced extraction of metadata from unstructured PDF payloads.",
      progress: Math.floor(Math.random() * 40) + 50, // fluctuate between 50 and 90
      eta_seconds: 12,
      worker_id: "942"
    };
  },
  
  getAutomationQueue: async () => {
    await delay(400);
    return {
      data: [
        {
          task_id: "task_890",
          task_name: "Neural-Sentiment-Analysis",
          batch_id: "88219",
          status: "queued",
          estimated_time: "45s"
        },
        {
          task_id: "task_891",
          task_name: "Sync-Gmail-Inbox-Primary",
          batch_id: "88220",
          status: "delayed",
          estimated_time: "2m 30s"
        }
      ]
    };
  },
  
  getAutomationHistory: async () => {
    await delay(400);
    return {
      data: [
        {
          id: "hist_5521",
          task_name: "User-Auth-Audit",
          status: "success",
          description: "Success: 1,202 logs scrubbed and validated.",
          timestamp: new Date(Date.now() - 5 * 60000).toISOString()
        },
        {
          id: "hist_5520",
          task_name: "Report-Generation-Weekly",
          status: "success",
          description: "Generated 14 PDFs and dispatched.",
          timestamp: new Date(Date.now() - 45 * 60000).toISOString()
        },
        {
          id: "hist_5519",
          task_name: "Webhook-Delivery-Client-B",
          status: "failed",
          description: "Timeout after 3 attempts.",
          timestamp: new Date(Date.now() - 120 * 60000).toISOString()
        }
      ]
    };
  }
};

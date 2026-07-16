# 03 — API Contract
## Expected Endpoints (Draft — To Be Confirmed With Aakash)

This document lists every endpoint the dashboard is expected to call, with
example request/response shapes. These are drafted based on the module
requirements — actual field names must be confirmed with Aakash before final
integration. Using these as a starting contract prevents Antigravity from
inventing its own field names that won't match the real backend later.

---

## 1. Dashboard Overview

### `GET /dashboard/summary`
Returns aggregated stats for the KPI cards and chart.

**Response**
```json
{
  "total_workflows": 1284,
  "active_workflows": 842,
  "emails_processed": 45200,
  "successful_executions": 44150,
  "failed_executions": 12,
  "pending_jobs": 156,
  "system_health_percent": 99.9,
  "email_volume_series": [
    { "time": "08:00", "incoming": 120, "automated": 95 },
    { "time": "10:00", "incoming": 180, "automated": 150 }
  ]
}
```

### `GET /dashboard/recent-activity`
Returns the list shown in the Recent Activity section.

**Response**
```json
{
  "data": [
    {
      "id": "act_001",
      "type": "workflow_success",
      "title": "Workflow \"Invoice_Parser_v2\" executed successfully",
      "description": "Processed 14 internal attachments from AP@enterprise.com",
      "timestamp": "2026-07-16T09:42:00Z",
      "status": "success"
    }
  ]
}
```

---

## 2. Workflow Control

### `GET /workflows`
List workflows, with optional filters.

**Query params:** `status`, `search`, `page`, `page_size`, `sort_by`

**Response**
```json
{
  "data": [
    {
      "id": "wf_98231",
      "name": "Data Ingestion Pipeline v4",
      "status": "running",
      "trigger_type": "cron",
      "schedule": "*/10 * * * *",
      "last_run": "2026-07-16T09:50:00Z",
      "category_filter": "Billing Complaint",
      "destination_team": "Finance"
    }
  ],
  "total": 24,
  "page": 1,
  "page_size": 10
}
```

### `POST /workflows`
Create a new workflow.

**Request**
```json
{
  "name": "New Workflow",
  "trigger_type": "webhook",
  "schedule": null,
  "category_filter": "Support Ticket",
  "destination_team": "Support"
}
```

**Response** — returns the created object with a generated `id` and
`status: "disabled"` by default.

### `PUT /workflows/{id}`
Edit an existing workflow. Same body shape as POST.

### `DELETE /workflows/{id}`
Delete a workflow. **Response:** `{ "success": true }`

### `POST /workflows/{id}/start`
### `POST /workflows/{id}/stop`
Start/stop a workflow. **Response:** returns updated `status` field.

---

## 3. Email Monitoring

### `GET /emails`
**Query params:** `status` (sent/delivered/pending/failed/bounced), `search`,
`page`, `page_size`

**Response**
```json
{
  "data": [
    {
      "id": "em_10234",
      "recipient": "marcus.kane@enterprise.io",
      "subject": "Critical System Alert: Node Failure in Cluster-A7",
      "category": "Infrastructure",
      "status": "failed",
      "sent_time": "2026-07-16T09:42:11Z",
      "retry_count": 1
    }
  ],
  "total": 1248,
  "page": 1,
  "page_size": 20
}
```

### `POST /emails/{id}/retry`
Retry a failed email.

**Response:** `{ "id": "em_10234", "status": "pending", "retry_count": 2 }`

---

## 4. Automation Activity

### `GET /automation/current-task`
Returns the currently-running task, if any.

**Response**
```json
{
  "task_id": "task_889",
  "task_name": "Invoice-Parsing-Cluster-B7",
  "description": "Advanced extraction of metadata from unstructured PDF payloads.",
  "progress": 68,
  "eta_seconds": 12,
  "worker_id": "942"
}
```

### `GET /automation/queue`
**Response**
```json
{
  "data": [
    {
      "task_id": "task_890",
      "task_name": "Neural-Sentiment-Analysis",
      "batch_id": "88219",
      "status": "queued",
      "estimated_time": "45s"
    }
  ]
}
```

### `GET /automation/history`
Recent execution history for the timeline.

**Response**
```json
{
  "data": [
    {
      "id": "hist_5521",
      "task_name": "User-Auth-Audit",
      "status": "success",
      "description": "Success: 1,202 logs scrubbed and validated.",
      "timestamp": "2026-07-16T14:22:01Z"
    }
  ]
}
```

---

## 5. Shared / Cross-Module

### `GET /categories`
Returns Sprint 1's 22-category list as reference data — fetched, not hardcoded.
See `04_data_reference.md` for full source content.

**Response**
```json
{
  "data": [
    { "category": "Billing Complaint", "type": "Customer", "department": "Finance", "priority": "High" },
    { "category": "Server Downtime Alert", "type": "Internal", "department": "Engineering", "priority": "Critical" }
  ]
}
```

---

## Notes for Integration

- All list endpoints should support `page` and `page_size` — never assume small
  datasets.
- All endpoints should return a consistent error shape on failure, e.g.
  `{ "error": true, "message": "..." }`, so the frontend can handle errors
  uniformly across modules.
- Timestamps are expected in ISO 8601 format (UTC), formatted client-side for
  display.
- Field names above are a starting proposal — confirm actual names with Aakash
  before final integration, and update this file to match what's actually built.

---

## 6. Authentication (Consumed, Not Built by Vinodh)

Every request from the dashboard is expected to include an auth token, provided
by Aakash's authentication system:

```
Authorization: Bearer <token>
```

- If a request returns `401 Unauthorized`, the frontend should redirect to the
  login screen — this behavior should be handled once, in a shared API client
  wrapper or the shared `useLiveData` hook, not repeated per call.
- Role-based visibility (e.g. only Admin can see "Create Workflow") is expected
  to be provided via the authenticated user's role, likely returned from a
  `GET /me` or similar endpoint — to be confirmed with Aakash.

---

## 7. Standard Error Response Shape

All endpoints should fail in a consistent, predictable way so the frontend can
handle errors uniformly instead of writing custom handling per endpoint.

```json
{
  "error": true,
  "code": "VALIDATION_ERROR",
  "message": "Workflow name is required."
}
```

| HTTP Status | Meaning | Frontend Behavior |
|---|---|---|
| 400 | Bad request / validation error | Show inline form error |
| 401 | Not authenticated | Redirect to login |
| 403 | Not authorized (wrong role) | Show "not permitted" message, hide the action |
| 404 | Resource not found | Show empty state |
| 500 | Server error | Show generic retry banner, log to console |

---

## 8. Pagination Convention

All list endpoints follow the same query parameter and response pattern, so the
shared `DataTable` and `Pagination` components work identically across Workflow
Control and Email Monitoring without per-module customization.

**Query params:** `?page=1&page_size=20`

**Response wrapper (always the same shape):**
```json
{
  "data": [ /* array of records */ ],
  "total": 1248,
  "page": 1,
  "page_size": 20
}
```

---

## 9. API Versioning Note

No versioning prefix (e.g. `/v1/`) has been agreed yet. Recommendation: confirm
with Aakash whether endpoints will be prefixed (`/api/v1/workflows`) before
integration — adding this early is a simple decision, but a scattered fix if
discovered only after both sides have already built against un-prefixed URLs.

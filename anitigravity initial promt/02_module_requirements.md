# 02 — Module Requirements
## Vinodh's 4 Modules — Features, Fields, Actions

---

## Module 1 — Dashboard Overview

### Purpose
Give an admin an instant answer to "is everything okay right now?" Purely a
summary screen — no direct database connection, it aggregates data already
fetched by the other 3 modules.

### Features
- Total Workflows
- Active Workflows
- Running Jobs
- Emails Processed
- Successful Executions
- Failed Executions
- Pending Jobs
- System Health Summary

### Fields (per KPI card)
- `label` (string)
- `value` (number)
- `trend` (optional — % change, up/down indicator)
- `status` (optional — success / warning / error, for health-related cards)

### UI Components
- KPI Cards (4–6 in a grid)
- One chart (bar or line — e.g. emails processed over time)
- Recent Activity list (icon + text + timestamp, not a table)

### Actions
- Manual refresh (icon button)
- No create/edit/delete actions on this screen — strictly read-only

### States to Handle
- Loading: skeleton cards while fetching
- Empty: "No activity yet" if Recent Activity is empty
- Error: inline message if summary fetch fails, don't crash other cards

---

## Module 2 — Workflow Control Panel

### Purpose
Where an admin creates and manages automation rules — the only module with real
CRUD actions.

### Features
- Create Workflow
- Edit Workflow
- Delete Workflow
- Enable / Disable Workflow
- Start / Stop Workflow
- Workflow Status
- Trigger Configuration
- Schedule Management

### Fields (per workflow record)
- `id` (string/uuid)
- `name` (string)
- `status` (enum: running / active / paused / disabled)
- `trigger_type` (enum: cron / webhook / api_poll / manual)
- `schedule` (string, e.g. cron expression, nullable if trigger is not cron)
- `last_run` (timestamp, nullable)
- `category_filter` (optional — references Sprint 1 category list, see
  `04_data_reference.md`)
- `destination_team` (optional — from Sprint 1 routing matrix)

### UI Components
- Data Table: Workflow Name, Status (badge), Trigger Type, Last Run, Actions
- Filter tabs: All / Running / Paused / Disabled
- Search bar
- "Create Workflow" primary button → opens modal/side panel (not a full page)
- Sort dropdown (e.g. "Sort by Last Run")
- Pagination

### Actions
- Create (modal form)
- Edit (modal form, pre-filled)
- Delete (confirmation dialog required — never delete without confirming)
- Start / Stop (icon buttons inline in table row)
- Enable / Disable (toggle)

### States to Handle
- Loading: table skeleton
- Empty: "No workflows yet — create your first one" with a call-to-action button
- Error: inline banner, table stays visible with last-known data if possible
- Form validation errors: shown inline in the modal, modal stays open

---

## Module 3 — Email Monitoring

### Purpose
Where an admin checks whether emails actually sent, and intervenes on failures.

### Features
- Sent Emails
- Delivered Emails
- Pending Emails
- Failed Emails
- Bounce Reports
- Retry Status

### Fields (per email record)
- `id` (string/uuid)
- `recipient` (string, email address)
- `subject` (string)
- `category` (string — from Sprint 1's 22-category list)
- `status` (enum: sent / delivered / pending / failed / bounced)
- `sent_time` (timestamp)
- `retry_count` (number, nullable)

### UI Components
- Filter tabs: All / Sent / Delivered / Pending / Failed / Bounced
- Data Table: Recipient, Subject, Category, Status (badge), Sent Time, Actions
- Search bar (recipient or subject)
- Pagination (expect large volume — thousands of rows over time)
- Retry button (inline, only visible on Failed rows)

### Actions
- Retry (only on failed emails)
- View details (optional expandable row or side panel)
- No create/delete — this module is read + retry only, emails aren't manually
  created here

### States to Handle
- Loading: table skeleton
- Empty: "No emails found" per filter tab
- Error: inline banner if fetch fails
- Retry in progress: button shows loading state, disabled during retry call

---

## Module 4 — Automation Activity

### Purpose
Shows what the system is doing right now — the only module that should feel
genuinely "live," not just refreshed.

### Features
- Running Processes
- Execution Queue
- Current Task
- Last Execution
- Next Scheduled Execution
- Processing Time

### Fields (per activity/task record)
- `task_id` (string)
- `task_name` (string)
- `status` (enum: processing / queued / delayed / completed / failed)
- `progress` (number 0–100, nullable — only for currently-running task)
- `eta_seconds` (number, nullable)
- `estimated_time` (string, for queued items)
- `timestamp` (for history/timeline items)

### UI Components
- "Current Task" highlight card (larger, distinct style, progress bar, ETA)
- Execution Queue (table or list: Task Name, Status, Est. Time)
- Recent History / Activity Timeline (vertical, most recent first)
- Small "Last updated Xs ago" indicator to signal live data without a manual
  refresh button

### Actions
- No create/edit/delete — strictly observational
- Optional: "View Full Logs" link (may route to Aakash's Logs module)

### States to Handle
- Loading: skeleton for current task card and queue
- Empty: "No active processes" if queue is empty
- Error: inline message, don't let a polling failure spam retries silently
- Live update: current task card updates in place, don't re-render the whole
  screen on each poll

---

## Shared Across All 4 Modules

- Consistent sidebar navigation: Dashboard, Workflows, Email Monitoring,
  Automation (fixed order, identical across all screens)
- Consistent status badge colors/labels for the same meaning across modules
  (e.g. "Failed" always looks the same, everywhere)
- Consistent date/time formatting via one shared utility function
- Consistent card style, spacing, and typography — reused component library, not
  rebuilt per module

---

## Component Reuse Map

This maps every reusable UI piece to the modules that use it — build each of
these **once**, in a shared `components/` folder, before building module screens.

| Component | Used In | Notes |
|---|---|---|
| `KpiCard` | Dashboard Overview, Automation Activity (queue stats) | Label + value + optional trend |
| `StatusBadge` | All 4 modules | Same colors/labels for the same status everywhere |
| `DataTable` | Workflow Control, Email Monitoring | Sortable, paginated, supports inline actions |
| `FilterTabs` | Email Monitoring, Workflow Control | Horizontal tab-style filter bar |
| `SearchBar` | Workflow Control, Email Monitoring | Debounced input, avoid firing a request per keystroke |
| `Modal` | Workflow Control (Create/Edit) | Reused for any future form-based module |
| `ConfirmDialog` | Workflow Control (Delete) | Generic yes/no confirmation, reusable anywhere destructive actions exist |
| `ActivityTimeline` | Dashboard Overview (Recent Activity), Automation Activity (Recent History) | Vertical list, icon + text + timestamp |
| `EmptyState` | All 4 modules | Consistent "nothing here yet" pattern |
| `LoadingSkeleton` | All 4 modules | Consistent loading placeholder, not a spinner |
| `Pagination` | Workflow Control, Email Monitoring | Shared page-size and page-number logic |
| `useLiveData` (hook, not component) | All 4 modules | Fetch + loading + error + optional polling interval |

---

## Interaction Detail — What Happens When Things Go Wrong

Being explicit about failure behavior per module, not just success behavior:

**Workflow Control**
- If Create/Edit submit fails: keep the modal open, show the error inline near
  the submit button, don't lose the user's typed input.
- If Start/Stop fails: revert the status badge back to its previous state and
  show a small inline error, don't leave the UI in a false "changed" state.

**Email Monitoring**
- If Retry fails: show an inline error on that row specifically, don't block the
  rest of the table.
- If the list fetch fails entirely: show a retry button in place of the table,
  not a blank page.

**Automation Activity**
- If a poll fails once: fail silently and try again on the next interval — don't
  show an error for a single missed poll.
- If polling fails repeatedly (e.g. 3 times in a row): show a small "connection
  issue" indicator near the "Last updated" text.

**Dashboard Overview**
- If one KPI card's data is missing: show that card in an empty/dash state
  (e.g. "—"), don't let one missing field break the entire grid.


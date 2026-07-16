# 01 — Project Brief
## AI-Powered Email Automation System — Sprint 4 Dashboard

---

## 1. What This Project Is

Utservio is building an AI-powered Email Automation System that automates customer
and internal communication through intelligent workflows. This is not a single-sprint
project — it is being built in stages, and this document exists so any tool or person
picking up Sprint 4 understands the full chain, not just this one piece.

---

## 2. How We Got Here — Sprint 1 → Sprint 2 → Sprint 4

### Sprint 1 — Email Classification & Routing Logic (Completed)
Sprint 1 produced the business logic that the rest of the system depends on:

- **22 email categories** (12 Customer-facing, 10 Internal), each mapped to a
  Department, Intent, Priority, and Sentiment.
- A **routing matrix** — for every category, which team it goes to, what priority
  it carries, and whether it needs escalation.
- A **classification framework** — the rules (keyword, sender, sentiment, structural
  signals, confidence threshold) used to decide which category an email belongs to.
- A list of **automation opportunities** — Classification, Tagging, Assignment,
  Reply, Escalation — phased by what to automate first.

This sprint did not write production code. It defined the rules the system now
follows.

### Sprint 2 — Gmail Data Collection Engine (Completed)
Sprint 2 built the pipeline that actually collects data:

- Gmail OAuth 2.0 authentication (secure, no password storage)
- Gmail API integration to pull emails and attachments
- Full Sync (first-time complete mailbox pull) and Incremental Sync (only new
  emails, using Gmail History IDs)
- Data stored in Supabase PostgreSQL: `emails`, `attachments`, `sync_runs`,
  `sync_logs`, `sync_errors`
- Duplicate prevention via unique Gmail Message IDs

At the end of Sprint 2, real email data exists in the database — but nobody can see
it. There is no interface.

### Sprint 4 — Dashboard & Control Panel (This Project)
Sprint 4 builds the human-facing layer on top of Sprint 2's data, using Sprint 1's
categories and routing logic as reference data. Specifically:

- Sprint 1's 22 categories become filter/tag options inside Email Monitoring.
- Sprint 1's routing matrix becomes the logic behind Workflow Control's trigger
  configuration (e.g. "if category = Billing Complaint → route to Finance,
  priority High").
- Sprint 2's tables (`emails`, `sync_runs`, `sync_logs`, `sync_errors`) are the
  actual data source the dashboard reads from.

**Important distinction:** automatic classification (AI reading an email and
assigning it a category automatically) is NOT built yet. That is future scope.
Right now, categories exist as reference data the dashboard can filter and display
by — not as a live AI process.

---

## 3. My Role in This Sprint

**Name:** Vinodh
**Ownership:** Operational Dashboard Layer

I own the four modules an admin uses daily to run and watch the system:

1. Dashboard Overview
2. Workflow Control
3. Email Monitoring
4. Automation Activity

Plus the shared UI/UX layer that ties them together (sidebar, header, routing,
design system, reusable components).

**Not my scope (owned by teammate Aakash):** Email Template Management, Logs &
Activity, User Management, System Configuration, System Monitoring, and the
backend/database/auth layer underneath everything.

---

## 4. Tech Stack

| Layer | Technology | Reasoning |
|---|---|---|
| Frontend | React + Vite | Fast builds, component reuse across 4 modules |
| Styling | Tailwind CSS | Consistent design system, no CSS sprawl |
| Routing | React Router | Clean navigation across dashboard sections |
| Backend (consumed, not built by me) | FastAPI REST | Matches what Sprint 2 already runs on |
| Database (consumed, not built by me) | PostgreSQL (Supabase) | Sprint 2's data already lives here |
| Live data strategy | Polling (5–10s) by default | Simplest tool that solves the freshness requirement |
| Live data strategy (conditional) | Server-Sent Events | Only for Automation Activity, only if polling proves too slow |

**Explicitly not using:** WebSockets (unnecessary for receive-only data), Redux
(plain React state + one shared hook is enough at this scale).

---

## 5. Build Order (Why This Order, Not Screen Order)

Dashboard Overview has no data source of its own — it purely aggregates the other
three modules. Building it first would mean rebuilding it once the real data shapes
from the other modules are known. So the order is:

1. Shared layout shell (sidebar, header, routing) — everything else plugs into this
2. Shared component library (KPI Card, Data Table, Status Badge, Filter Bar,
   `useLiveData` hook)
3. Workflow Control — connects directly to Sprint 2 / new `workflows` table
4. Email Monitoring — connects directly to Sprint 2's `emails`, `sync_errors` tables
5. Automation Activity — connects to `sync_runs`, `sync_logs`
6. Dashboard Overview — built last, since it aggregates 1–5
7. Integration with real backend (replacing mocked data)
8. Testing (functional, responsive, empty/error states, large-dataset behavior)

---

## 6. Design Style

Flat / minimal enterprise style — similar to GitHub, Linear, Vercel. High contrast,
clean typography, subtle borders instead of heavy shadows. No glassmorphism, no
neumorphism, no gradients. One accent color used sparingly for primary actions and
active states.

**Reasoning:** this is a data-heavy operational dashboard. Clarity and scan-speed
matter more than a trend-driven visual style. Admins need to read status at a
glance, not admire the UI.

---

## 7. Assumptions

- Backend APIs (built by Aakash) will return data in the format agreed in
  `03_api_contract.md`
- Authentication/login system will already exist when I integrate — I consume it,
  I don't build it
- Sprint 2's data collection is accurate and reliable — I am not re-validating it
- Users access the dashboard from modern desktop/tablet browsers (Chrome, Edge)
- Data volumes during development/testing are reasonable, not full production scale

## 8. Known Limitations (Current Scope)

- Data updates via polling, not true real-time (a few seconds' delay is expected)
- No offline support — requires an active connection
- Large-dataset performance (thousands of rows) not yet tested
- English only, no localization
- Web-responsive, not a native mobile app
- Automatic AI classification is not built — categories are reference data only,
  displayed/filtered, not auto-assigned

---

## 9. Glossary (For Anyone New to This Project)

| Term | Meaning |
|---|---|
| Workflow | An automation rule — "when X happens, do Y" |
| Sync | The process of pulling new emails from Gmail into the database |
| Full Sync | First-time import of an entire mailbox |
| Incremental Sync | Ongoing sync that only pulls new/changed emails since last check |
| History ID | Gmail's bookmark mechanism used for incremental sync |
| Polling | Repeatedly checking an API for new data on a timer |
| SSE (Server-Sent Events) | A way for the backend to push live updates without the frontend asking repeatedly |
| KPI Card | A small summary card showing one key number (e.g. "Total Workflows: 1,284") |
| Producer–Consumer Architecture | Aakash's modules "produce" data (logs, config, health), my modules "consume" and display it |
| Reference Data | Data that doesn't change often and is fetched, not hardcoded (e.g. Sprint 1's categories) |

---

## 10. Team & Ownership Contacts

| Area | Owner | Notes |
|---|---|---|
| Dashboard Overview, Workflow Control, Email Monitoring, Automation Activity, UI/UX | Vinodh | This document's author |
| Email Templates, Logs, User Management, System Config, System Monitoring, Backend/Auth | Aakash | Confirm API contract details directly with him |
| Sprint 1 category & routing matrix (source of truth) | Original Sprint 1 output | See `04_data_reference.md` — confirm final values before integration |

---

## 11. How This Document Should Be Used

This file is meant to be read first, before any module requirement or API
contract. It answers "why does this exist" so that later documents (which
answer "what exactly to build") make sense in context. If a future contributor
or tool only reads one document in this set, it should be this one.


# 04 — Data Reference
## Sprint 1 Category & Routing Matrix (Reference Data)

---

## Important Note Before Using This File

This is a **trimmed, representative version** of Sprint 1's actual
`email-category-matrix.xlsx` and `routing-matrix.xlsx`. The real files contain
the authoritative 22 categories with full detail (Department, Intent, Priority,
Sentiment, Required Action, and a worked example per category).

**Before final integration:** replace the placeholder rows below with the exact
values from the real Sprint 1 spreadsheets. This file exists so Antigravity
understands the *shape* of this reference data and treats it as something
fetched from `GET /categories`, not hardcoded text in the UI.

---

## Why This Data Matters for Sprint 4

- These categories appear as **filter/tag options** in Email Monitoring.
- The routing matrix (Destination Team, Priority, Escalation) is the logic
  behind Workflow Control's **Trigger Configuration** — e.g. a workflow rule
  like "if category = Billing Complaint → route to Finance, priority High."
- Categories must be fetched from the API (`GET /categories`), never hardcoded
  as a fixed list in frontend code — if Sprint 1's matrix changes, the UI should
  update without a code change.

---

## Category Matrix — Trimmed Example (12 Customer-Facing)

| Category | Department | Priority | Sentiment | Required Action |
|---|---|---|---|---|
| Billing Complaint | Finance | High | Negative | Investigate & Respond |
| Refund Request | Finance | Medium | Neutral | Process Refund |
| Product Inquiry | Sales | Low | Neutral | Send Info / Route to Sales |
| Technical Support Request | Engineering | High | Negative | Assign to Support Engineer |
| Account Access Issue | Support | High | Negative | Reset / Verify Access |
| Subscription Cancellation | Retention | Medium | Negative | Route to Retention Team |
| Order Status Inquiry | Operations | Low | Neutral | Provide Status Update |
| Delivery Complaint | Operations | High | Negative | Investigate Logistics |
| Positive Feedback | Marketing | Low | Positive | Log / Optional Response |
| Partnership Inquiry | Business Dev | Medium | Neutral | Route to BD Team |
| Legal / Compliance Concern | Legal | Critical | Negative | Escalate Immediately |
| Spam / Irrelevant | — | Low | Neutral | Archive / No Action |

*(...remaining Customer categories to be filled from the actual Sprint 1 file)*

## Category Matrix — Trimmed Example (10 Internal)

| Category | Department | Priority | Sentiment | Required Action |
|---|---|---|---|---|
| Server Downtime Alert | Engineering | Critical | Negative | Escalate to On-Call |
| Internal Policy Update | HR | Low | Neutral | Broadcast / Archive |
| Access Request (Internal) | IT | Medium | Neutral | Approve / Provision |
| System Backup Notification | Engineering | Low | Neutral | Log Only |
| Budget Approval Request | Finance | Medium | Neutral | Route to Finance Lead |
| Employee Onboarding | HR | Medium | Positive | Trigger Onboarding Workflow |
| Security Incident Report | Security | Critical | Negative | Escalate Immediately |
| Vendor Invoice | Finance | Medium | Neutral | Route to AP Team |
| Internal Escalation | Varies | High | Negative | Route to Relevant Team Lead |
| Meeting / Scheduling | — | Low | Neutral | No Automated Action |

*(...remaining Internal categories to be filled from the actual Sprint 1 file)*

---

## Routing Matrix Shape (Reference Structure)

Each category maps to:

```json
{
  "category": "Billing Complaint",
  "destination_team": "Finance",
  "priority_level": "High",
  "expected_action": "Investigate & Respond within 24h",
  "escalation_required": true
}
```

This is the object shape `GET /categories` (or a dedicated `GET /routing-matrix`
endpoint) should return — Workflow Control's trigger configuration form should
populate its "Category" and "Destination Team" dropdowns from this data, not
from a hardcoded list.

---

## Classification Framework (Context Only — Not Built in This Sprint)

Sprint 1 also defined the logic for *how* an email would be automatically
classified, using six fields:

1. Category
2. Department
3. Intent
4. Priority
5. Sentiment
6. Required Action

Classification signals considered: keyword matching, sender address/domain,
sentiment analysis, structural signals (subject line patterns, formatting), and
a confidence threshold below which an email is flagged for manual review.

**This automatic classification engine is not part of Sprint 4.** The dashboard
only displays and filters by category — it does not run classification logic.
This section is included so the reasoning behind the category list is
understood, and so the UI leaves room for a future "Suggested Category" or
"Confidence Score" field without requiring a redesign.

---

## How to Finalize This File

1. Open the real `email-category-matrix.xlsx` and `routing-matrix.xlsx` from
   Sprint 1.
2. Replace the two tables above with the complete, accurate 22 rows.
3. Confirm with Aakash whether this becomes its own database table
   (`email_categories`) or lives as static reference data returned by the API.
4. Update `03_api_contract.md`'s `GET /categories` example response to match
   the final, real field names.



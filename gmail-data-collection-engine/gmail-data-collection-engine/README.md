# Utservio Gmail Communication Data Collection Engine

A secure, production-grade backend service that connects to Gmail accounts via Desktop OAuth 2.0, synchronizes emails incrementally, extracts metadata and attachments, and stores all processed data in **Supabase PostgreSQL** and **Supabase Storage**.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup Guide](#setup-guide)
- [Running the Server](#running-the-server)
- [Running the Automated Scheduler](#running-the-automated-scheduler)
- [CLI Scripts](#cli-scripts)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Security Considerations](#security-considerations)
- [Sync Architecture](#sync-architecture)
- [Configuration Reference](#configuration-reference)
- [Documentation](#documentation)
- [License](#license)

---

## Architecture Overview

```
┌─────────────────────┐
│   Gmail API         │
│  (gmail.readonly)   │
└────────┬────────────┘
         │ Desktop OAuth 2.0
         ▼
┌─────────────────────┐     ┌──────────────────────┐
│   FastAPI Server    │     │   APScheduler        │
│   (REST API)        │     │   (BlockingScheduler) │
│                     │     │                      │
│  ┌───────────────┐  │     │  Polls mailboxes     │
│  │ SyncOrchestrator │◄────┤  every N minutes     │
│  └───────┬───────┘  │     └──────────────────────┘
│          │          │
│  ┌───────▼───────┐  │
│  │ Email Parser  │  │
│  │ Attachment    │  │
│  │ Processor     │  │
│  └───────┬───────┘  │
└──────────┼──────────┘
           │
     ┌─────▼──────┐    ┌─────────────────────┐
     │ Supabase   │    │ Supabase Storage    │
     │ PostgreSQL │    │ (email-attachments) │
     └────────────┘    └─────────────────────┘
```

---

## Features

| Feature | Status |
|---|---|
| Gmail Desktop OAuth 2.0 authentication | ✅ |
| Scope-validated, auto-refreshing token management | ✅ |
| Full & incremental email sync (via Gmail `historyId`) | ✅ |
| MIME-recursive email body extraction (text/plain, text/html) | ✅ |
| Header extraction (From, To, Cc, Bcc, Subject, Date) | ✅ |
| Attachment extraction with type/size security filtering | ✅ |
| Supabase Storage upload with retry logic | ✅ |
| Atomic distributed mailbox locking with TTL recovery | ✅ |
| APScheduler automated incremental sync | ✅ |
| Detailed `sync_runs` audit trail with per-run metrics | ✅ |
| Granular `sync_errors` per failed email/attachment | ✅ |
| Soft-deletion & data retention lifecycle fields | ✅ |
| AI-readiness fields (`ai_processing_status`, `raw_email_json`) | ✅ |
| Row Level Security enabled on all tables | ✅ |
| Comprehensive pytest test suite | ✅ |

---

## Project Structure

```
gmail-data-collection-engine/
├── app/
│   ├── api/                    # FastAPI route handlers
│   │   ├── auth.py             # POST /auth/gmail/connect
│   │   ├── emails.py           # GET /emails
│   │   ├── health.py           # GET /health
│   │   ├── mailboxes.py        # GET /mailboxes
│   │   └── sync.py             # POST /sync/{id}
│   ├── auth/
│   │   └── gmail_oauth.py      # Desktop OAuth flow & token management
│   ├── clients/
│   │   └── supabase_client.py  # Supabase Storage client & retry upload
│   ├── db/
│   │   ├── base.py             # SQLAlchemy declarative base
│   │   └── session.py          # Engine & SessionLocal factory
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── attachment.py
│   │   ├── email.py
│   │   ├── mailbox_account.py
│   │   ├── sync_error.py
│   │   ├── sync_log.py
│   │   └── sync_run.py
│   ├── providers/
│   │   ├── base_provider.py    # Abstract base class
│   │   └── gmail_provider.py   # Gmail API integration
│   ├── services/               # Business logic layer
│   │   ├── attachment_service.py
│   │   ├── email_service.py
│   │   ├── mailbox_service.py
│   │   ├── sync_orchestrator.py # Central sync engine with locking
│   │   └── sync_service.py
│   ├── utils/
│   │   ├── attachment_utils.py  # File safety, base64 decode, path gen
│   │   ├── gmail_parser.py      # Gmail JSON → structured dict parser
│   │   └── sanitize_gmail_payload.py
│   ├── config.py               # Pydantic Settings (env-driven)
│   └── main.py                 # FastAPI app entrypoint
├── docs/                       # Technical documentation
├── migrations/                 # SQL migration scripts
├── scripts/                    # CLI tools
│   ├── authenticate_gmail.py   # One-time OAuth setup
│   ├── manual_sync.py          # On-demand sync trigger
│   └── run_scheduler.py        # Background automated sync
├── tests/                      # pytest test suite
├── .env.example                # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Prerequisites

- **Python** 3.10+
- **Supabase** project with PostgreSQL database
- **Google Cloud** project with Gmail API enabled and Desktop OAuth credentials
- **pip** (or a virtual environment manager)

---

## Setup Guide

### 1. Clone & Install

```bash
git clone <repository-url>
cd gmail-data-collection-engine
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:
- `DATABASE_URL` — Your Supabase PostgreSQL connection string
- `SUPABASE_URL` — Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` — Service role key (not the anon key)
- `TOKEN_ENCRYPTION_KEY` — A random 32-char hex string

### 3. Run Database Migrations

Execute the migration files in order against your Supabase SQL Editor:

```
migrations/001_initial_schema.sql
migrations/002_add_auth_mode_constraint.sql
migrations/003_add_locking_and_sync_tracking.sql
```

### 4. Set Up Google OAuth Credentials

See [docs/oauth-setup.md](docs/oauth-setup.md) for detailed instructions.

```bash
mkdir secrets
# Move your downloaded credentials JSON to:
# secrets/credentials.json
```

### 5. Authenticate Gmail Account

```bash
python scripts/authenticate_gmail.py
```

This opens a browser for OAuth consent, saves `secrets/token.json`, and registers the mailbox in the database.

---

## Running the Server

```bash
uvicorn app.main:app --reload
```

Access the interactive API documentation at: **http://localhost:8000/docs**

---

## Running the Automated Scheduler

Set `SCHEDULER_ENABLED=true` in `.env`, then:

```bash
python scripts/run_scheduler.py
```

The scheduler will poll all active mailboxes every `SYNC_INTERVAL_MINUTES` (default: 15) and run incremental syncs with full atomic locking.

---

## CLI Scripts

| Script | Purpose |
|---|---|
| `scripts/authenticate_gmail.py` | One-time Desktop OAuth authentication |
| `scripts/manual_sync.py` | Trigger a manual sync (`--mode full` or `--mode incremental`) |
| `scripts/run_scheduler.py` | Start the APScheduler automated background sync |
| `scripts/verify_sync_runs.py` | Query and display recent sync run metrics |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/auth/gmail/connect` | Verify Gmail OAuth connection |
| `GET` | `/mailboxes/` | List all registered mailbox accounts |
| `POST` | `/sync/{mailbox_account_id}` | Trigger manual sync for a mailbox |
| `GET` | `/emails/` | List synced emails (paginated via `skip` & `limit`) |

---

## Database Schema

Six tables with Row Level Security (RLS) enabled:

| Table | Purpose |
|---|---|
| `mailbox_accounts` | Registered Gmail accounts with sync status and lock state |
| `emails` | Synced email metadata, bodies, labels, and AI-readiness fields |
| `attachments` | File metadata and Supabase Storage references |
| `sync_runs` | Detailed per-sync audit log with metrics |
| `sync_logs` | Structured log entries per sync run |
| `sync_errors` | Granular error records per failed email/attachment |

See [migrations/001_initial_schema.sql](migrations/001_initial_schema.sql) for the complete schema.

---

## Testing

Run the full test suite:

```bash
pytest tests/ -v
```

Test coverage includes:
- **API endpoints**: Health, auth, mailboxes, sync triggers
- **Gmail parser**: Header extraction, body decoding, attachment detection, edge cases
- **Payload sanitization**: Attachment data stripping, nested multipart handling
- **Attachment utilities**: Filename sanitization, file type safety, base64 decoding, path generation
- **Sync locking**: Concurrent lock prevention, stale lock recovery
- **Scheduler config**: Environment variable loading and type validation
- **OAuth validation**: Credential file format checks, scope verification

---

## Security Considerations

| Area | Implementation |
|---|---|
| **OAuth Scope** | Strictly `gmail.readonly` — no write access to user email |
| **Credential Storage** | `credentials.json` and `token.json` stored in `secrets/` (gitignored) |
| **Token Handling** | Tokens never stored in the database; only local filesystem |
| **Credential Validation** | Rejects web-type OAuth credentials; enforces Desktop App type |
| **Attachment Filtering** | Blocks `.exe`, `.bat`, `.cmd`, `.sh`, `.js`, `.vbs`, `.msi` |
| **Attachment Size Limit** | Configurable max size (default 15 MB) |
| **Database Security** | Row Level Security enabled on all tables |
| **Environment Secrets** | All sensitive config via `.env` (gitignored) |
| **Input Sanitization** | Unknown fields stripped before database insert |
| **JSONB Sanitization** | Binary attachment data stripped from `raw_email_json` before storage |

---

## Sync Architecture

### Incremental Sync Flow

1. Scheduler or manual trigger initiates sync for a mailbox
2. **Atomic lock acquisition**: `UPDATE ... WHERE sync_status = 'connected' OR lock_expired`
3. Gmail `history.list()` fetches new message IDs since last `historyId`
4. If `historyId` expired (404), automatic fallback to full sync
5. Each message fetched, parsed, and saved individually
6. Attachments extracted, filtered, decoded, and uploaded to Supabase Storage
7. `sync_runs` record completed with full metrics
8. Lock released unconditionally in `finally` block

### Distributed Locking

- **Lock Token**: UUID stored on the mailbox row
- **TTL**: `sync_lock_expires_at` prevents permanent lock-up on crash
- **Stale Recovery**: Subsequent sync acquires if `sync_lock_expires_at < NOW()`

---

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | *required* | PostgreSQL connection string |
| `SUPABASE_URL` | *required* | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | *required* | Supabase service role key |
| `SUPABASE_STORAGE_BUCKET` | `email-attachments` | Storage bucket name |
| `ENVIRONMENT` | `development` | Runtime environment |
| `SCHEDULER_ENABLED` | `false` | Enable APScheduler background sync |
| `SYNC_INTERVAL_MINUTES` | `10` | Minutes between scheduled sync cycles |
| `SYNC_LOCK_TTL_MINUTES` | `20` | Lock expiry TTL in minutes |
| `MAX_EMAILS_PER_SYNC` | `50` | Max emails processed per sync run |
| `MAX_ATTACHMENTS_PER_SYNC` | `10` | Max attachments per sync run |
| `MAX_ATTACHMENT_SIZE_MB` | `15` | Max individual attachment size |
| `TOKEN_ENCRYPTION_KEY` | *required* | Encryption key for sensitive data |

---

## Documentation

| Document | Description |
|---|---|
| [OAuth Setup Guide](docs/oauth-setup.md) | Google Cloud credential configuration |
| [Desktop OAuth Flow](docs/gmail-desktop-oauth-flow.md) | Technical OAuth architecture |
| [Failure Recovery](docs/failure-recovery.md) | Error handling and sync rerun strategy |
| [Data Retention](docs/data-retention.md) | Soft-deletion and archiving policy |
| [AI Readiness](docs/ai-readiness.md) | Fields reserved for future AI processing |

---

## License

Proprietary — Utservio. All rights reserved.

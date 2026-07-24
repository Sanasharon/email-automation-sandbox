# Email Automation Dashboard

A full-stack enterprise platform for automating email workflows. Connects to Gmail via OAuth 2.0, synchronizes emails incrementally, and executes automated actions based on configurable rules with AI-powered processing.

## Architecture

```
┌──────────────────┐     ┌──────────────────┐
│   React Frontend │────▶│  FastAPI Backend  │
│   (Vite + Tailwind)│     │  (REST API + SSE) │
└──────────────────┘     └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │  Gmail   │ │ Supabase │ │ Supabase │
              │   API    │ │   DB     │ │ Storage  │
              └──────────┘ └──────────┘ └──────────┘
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite 8, Tailwind CSS 4, React Router 7, Chart.js, Lucide Icons |
| Backend | FastAPI, SQLAlchemy 2, APScheduler, Pydantic 2 |
| Database | PostgreSQL (Supabase) |
| Storage | Supabase Storage (email attachments) |
| Auth | Google OAuth 2.0, JWT tokens |
| AI | OpenAI, Gemini, Claude, Ollama (configurable) |

## Folder Structure

```
Email-Automation-Dashboard-final/
├── frontend/                    # React dashboard
│   ├── src/
│   │   ├── api/                 # API client & adapters
│   │   ├── components/          # Reusable UI components
│   │   ├── config/              # App configuration
│   │   ├── context/             # React context providers
│   │   ├── hooks/               # Custom hooks
│   │   ├── layouts/             # Page layouts
│   │   └── pages/               # Route pages
│   ├── Dockerfile
│   └── nginx.conf
├── gmail-data-collection-engine/
│   └── gmail-data-collection-engine/  # FastAPI backend
│       ├── app/
│       │   ├── api/             # Route handlers
│       │   │   ├── v1/          # Versioned API routes
│       │   │   └── *.py         # Legacy routes
│       │   ├── auth/            # OAuth & JWT
│       │   ├── middleware/       # Request processing
│       │   ├── models/          # SQLAlchemy models
│       │   ├── providers/       # Gmail API wrapper
│       │   ├── scheduler/       # Background sync
│       │   ├── schemas/         # Pydantic schemas
│       │   └── services/        # Business logic
│       ├── migrations/          # SQL migrations
│       ├── scripts/             # Utility scripts
│       ├── secrets/             # OAuth credentials (gitignored)
│       ├── Dockerfile
│       └── requirements.txt
├── docker-compose.yml
└── README.md
```

## Prerequisites

- **Python** 3.10+
- **Node.js** 18+
- **Supabase** project (PostgreSQL + Storage)
- **Google Cloud** project (Gmail API + OAuth credentials)

## Quick Start

### 1. Clone

```bash
git clone https://github.com/vinodh2008/Email-Automation-Dashboard-final.git
cd Email-Automation-Dashboard-final
```

### 2. Backend Setup

```bash
cd gmail-data-collection-engine/gmail-data-collection-engine

# Create virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (see Environment Variables below)

# Start server
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. Swagger docs at `/docs`.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at `http://localhost:5173`.

### 4. Docker Setup

```bash
# From project root
docker compose up --build
```

Frontend: `http://localhost:80`, Backend: `http://localhost:8000`

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Supabase service role key |
| `SUPABASE_STORAGE_BUCKET` | Yes | Storage bucket name (default: `email-attachments`) |
| `TOKEN_ENCRYPTION_KEY` | Yes | Fernet key for encrypting OAuth tokens |
| `JWT_SECRET` | Yes | Secret key for JWT token signing |
| `JWT_EXPIRES_IN_MINUTES` | No | Token expiry (default: 1440) |
| `CORS_ORIGINS` | No | Allowed origins JSON array |
| `SCHEDULER_ENABLED` | No | Enable background sync (default: false) |
| `SYNC_INTERVAL_MINUTES` | No | Sync interval (default: 10) |
| `MAX_EMAILS_PER_SYNC` | No | Max emails per sync run (default: 50) |
| `GOOGLE_CLIENT_SECRETS_FILE` | Yes | Path to OAuth credentials JSON |
| `GOOGLE_TOKEN_FILE` | Yes | Path to stored OAuth token |
| `ENVIRONMENT` | No | `development` or `production` |

Generate `TOKEN_ENCRYPTION_KEY`:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project or select existing
3. Enable **Gmail API** (APIs & Services > Library)
4. Create **OAuth 2.0 Client ID** (APIs & Services > Credentials)
   - Application type: **Desktop app**
5. Download the credentials JSON
6. Save as `secrets/credentials.json` in the backend directory
7. On first connection, the app will guide you through the OAuth flow

## Supabase Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **Settings > Database** and copy the connection string
3. Go to **Storage** and create a bucket named `email-attachments`
4. Go to **Settings > API** and copy the `service_role` key
5. Tables are created automatically on first startup via `ensure_full_schema()`

## Connecting Gmail

1. Open the dashboard at `http://localhost:5173`
2. Login with admin credentials
3. Go to **Settings > Gmail**
4. Click **Connect Gmail**
5. Complete the Google OAuth flow
6. The scheduler will start syncing emails automatically

## AI Provider Setup

1. Go to **Settings > AI Provider**
2. Click **Add Provider**
3. Configure:
   - **Provider Type**: OpenAI, Gemini, Claude, Ollama, or OpenAI-Compatible
   - **Model**: Select from presets or enter custom
   - **API Key**: Your API key
   - **Priority**: Lower number = higher priority
   - **Primary**: Mark as primary provider
4. Click **Test Connection** to verify
5. Mark as **Enabled**

Failover: If the primary provider fails, the system tries the next provider by priority.

## Prompt Templates

1. Go to **Templates**
2. Create templates with variables: `{{sender}}`, `{{subject}}`, `{{body}}`
3. Test with the **Test** button
4. Reference templates in workflows

## Workflows

1. Go to **Workflows**
2. Click **Create Workflow**
3. Set conditions (e.g., "Subject contains Invoice")
4. Set actions (e.g., "Label as Finance", "AI Process")
5. Enable the workflow

## Running Scheduler

The scheduler runs automatically when `SCHEDULER_ENABLED=true`. It:
- Polls active mailboxes every N minutes
- Performs incremental sync via Gmail History API
- Falls back to full sync if history is unavailable
- Logs all sync runs and errors

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/auth/login` | POST | Login |
| `/mailboxes/connect` | POST | Connect Gmail |
| `/mailboxes/disconnect` | POST | Disconnect Gmail |
| `/sync/{id}` | POST | Trigger manual sync |
| `/emails/` | GET | List emails |
| `/api/v1/workflows` | GET/POST | Workflow CRUD |
| `/api/v1/ai-providers` | GET/POST | AI provider CRUD |
| `/api/v1/prompt-templates` | GET/POST | Prompt template CRUD |
| `/api/v1/email-templates` | GET/POST | Email template CRUD |
| `/api/v1/users` | GET/POST | User management |
| `/api/v1/admin/roles` | GET/POST | Role management |
| `/api/v1/logs` | GET | System logs |

Full API docs at `http://localhost:8000/docs`.

## Database Tables

| Table | Purpose |
|-------|---------|
| `mailbox_accounts` | Gmail connection state |
| `emails` | Synced email metadata |
| `attachments` | Email attachment records |
| `sync_runs` | Sync execution history |
| `sync_errors` | Per-email/attachment errors |
| `workflows` | Automation rules |
| `workflow_executions` | Workflow run history |
| `ai_providers` | AI provider configuration |
| `ai_approvals` | AI draft review queue |
| `prompt_templates` | Reusable prompt templates |
| `email_templates` | Email templates |
| `system_logs` | Application logs |
| `users` | User accounts |
| `user_roles` | Role definitions |

## Testing

```bash
# Backend
cd gmail-data-collection-engine/gmail-data-collection-engine
pytest

# Frontend
cd frontend
npm run lint
```

## Deployment

### Backend (Render/Railway/AWS)

1. Set all environment variables
2. Point to `gmail-data-collection-engine/gmail-data-collection-engine/` as root
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Ensure `CORS_ORIGINS` includes your frontend domain

### Frontend (Vercel/Netlify/Cloudflare Pages)

1. Build command: `npm run build`
2. Output directory: `dist`
3. Set `VITE_API_BASE_URL` to your backend URL

### Docker Production

```bash
docker compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check `.env` has all required variables |
| 401 on API calls | Reconnect Gmail via Settings > Gmail |
| No emails syncing | Verify `SCHEDULER_ENABLED=true` and mailbox is connected |
| AI provider fails | Test connection in Settings > AI Provider |
| CORS errors | Add frontend URL to `CORS_ORIGINS` in `.env` |
| Port conflict | Change port in uvicorn command or docker-compose |

## Known Limitations

- Gmail API quota limits apply (250 units/user/day for free tier)
- Attachment download limited to 15MB per file
- Scheduler polls every 1 minute minimum
- AI processing requires valid API key from supported providers
- Password recovery not implemented (admin must reset)

## License

Proprietary — Utservio. All rights reserved.

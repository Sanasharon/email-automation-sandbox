# Email Automation Dashboard

A full-stack enterprise platform for automating email workflows, parsing incoming messages, categorizing them, and executing automated actions based on predefined rules. 

This repository contains both the frontend React dashboard and the backend FastAPI automation engine.

## 🚀 Tech Stack

- **Frontend**: React (Vite), React Router v6, Tailwind CSS, Lucide Icons, Recharts, Framer Motion.
- **Backend**: FastAPI, SQLAlchemy, APScheduler for background tasks, Google OAuth 2.0.
- **Database**: PostgreSQL (Supabase) and Supabase Storage for attachments.

## 📁 Repository Structure

- `/frontend` - The React application dashboard UI.
- `/gmail-data-collection-engine` - The FastAPI backend service.

---

## 🛠️ Quick Start Guide

Follow these steps to set up the project locally.

### 1. Prerequisites
- **Node.js** (v18+)
- **Python** (v3.10+)
- **Supabase** Project (for PostgreSQL and Storage)
- **Google Cloud Platform** Project (with Gmail API enabled and Desktop OAuth credentials)

### 2. Clone the Repository
```bash
git clone <your-repository-url>
cd Email-Automation-Dashboard-final
```

### 3. Backend Setup
The backend handles Google OAuth, email fetching, workflow automation, and exposes a REST API.

1. Navigate to the backend directory:
   ```bash
   cd gmail-data-collection-engine/gmail-data-collection-engine
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate



   <!-- important :::::: Before running the server,
    <!-- you must set up your Google Cloud credentials. Please follow the step-by-step instructions in the gmail-data-collection-engine/gmail-data-collection-engine/docs/oauth-setup.md file. --> -->
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to include your Supabase database URL and secret keys.*
5. Run database migrations in your Supabase SQL Editor (see `migrations/`).
6. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
   *API will be running at `http://localhost:8000`. Swagger docs at `/docs`.*

*(For more details, see the [Backend README](./gmail-data-collection-engine/gmail-data-collection-engine/README.md))*

### 4. Frontend Setup
The frontend provides the user interface for monitoring metrics, configuring workflows, and managing emails.

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node modules:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   *The dashboard will be available at `http://localhost:5173`.*

*(For more details, see the [Frontend README](./frontend/README.md))*

## 📜 Features
- **Real-time Metrics**: View processed emails, automation rates, and active workflows.
- **Workflow Engine**: Set conditional rules (IF email subject contains "Invoice") and actions (THEN label as "Finance").
- **Email Monitoring**: Inspect synced emails, attachments, and their processing status.
- **Admin Management**: RBAC and user management modules.

## 📄 License
Proprietary — Utservio. All rights reserved.

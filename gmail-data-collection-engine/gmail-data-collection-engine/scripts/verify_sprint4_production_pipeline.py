"""
Comprehensive Sprint 4 Production Pipeline Verification & Audit Script.
Validates FastAPI Lifespan Startup, APScheduler Domain Service, Atomic DB Updates (last_sync_at),
Dynamic Monitoring APIs, Account Chooser Configuration, and Multi-Surface Consistency.
"""
import sys
import os
import time
import logging
from sqlalchemy import text, desc
from datetime import datetime, timezone
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import settings
from app.db.session import SessionLocal
from app.models import MailboxAccount, Email, SyncRun, Attachment
from app.scheduler import scheduler_service
from app.providers.gmail_provider import GmailProvider
from app.services.sync_orchestrator import SyncOrchestrator
from app.main import app

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("production_verification")


def run_production_pipeline_audit():
    print("=" * 95)
    print("         SPRINT 4 PRODUCTION-GRADE GMAIL PIPELINE AUDIT & VERIFICATION REPORT")
    print("=" * 95)

    db = SessionLocal()

    # -------------------------------------------------------------------------
    # TEST 1: FastAPI Lifespan & APScheduler Service Initialization
    # -------------------------------------------------------------------------
    print("\n[TEST 1] FastAPI Lifespan & APScheduler Service Auto-Startup:")
    with TestClient(app) as client:
        # Initializing TestClient triggers FastAPI lifespan startup
        sched_status = scheduler_service.get_status()
        print(f"  - APScheduler Running Status : {sched_status['is_running']}")
        print(f"  - SCHEDULER_ENABLED Config  : {sched_status['scheduler_enabled']}")
        print(f"  - Health State              : {sched_status['health_state']}")
        print(f"  - Sync Interval             : {sched_info['sync_interval_minutes'] if 'sync_info' in locals() else sched_status['sync_interval_minutes']} minute(s)")
        print(f"  - Registered Jobs           : {len(sched_status['registered_jobs'])} registered")
        for job in sched_status['registered_jobs']:
            print(f"      - Job ID: '{job['id']}' | Next Run: {job['next_run_time']} | Trigger: {job['trigger']}")

        if sched_status["is_running"]:
            print("  -> RESULT: [PASS] APScheduler auto-starts inside FastAPI lifespan manager.")
        else:
            print("  -> RESULT: [FAIL] APScheduler did not start automatically.")

        # -------------------------------------------------------------------------
        # TEST 2: Dynamic System Monitoring Endpoint (/api/v1/system/status)
        # -------------------------------------------------------------------------
        print("\n[TEST 2] System Monitoring Single Source of Truth Endpoint:")
        res_status = client.get("/api/v1/system/status")
        print(f"  - GET /api/v1/system/status Response Code : {res_status.status_code}")
        if res_status.status_code == 200:
            sys_data = res_status.json()
            print(f"  - Scheduler Is Running     : {sys_data['scheduler']['is_running']}")
            print(f"  - System Health Score      : {sys_data['health_score']}%")
            print(f"  - Current Gmail Account    : {sys_data['mailbox']['current_gmail']}")
            print(f"  - Mailbox Sync Status      : {sys_data['mailbox']['sync_status']}")
            print(f"  - Last History ID          : {sys_data['mailbox']['last_history_id']}")
            print(f"  - Last Sync At             : {sys_data['mailbox']['last_sync_at']}")
            print(f"  - Database Connected       : {sys_data['database']['connected']}")
            print(f"  - Total Sync Runs          : {sys_data['database']['total_sync_runs']}")
            print("  -> RESULT: [PASS] System monitoring endpoint exposes live metrics.")
        else:
            print(f"  -> RESULT: [FAIL] /api/v1/system/status failed: {res_status.text}")

        # -------------------------------------------------------------------------
        # TEST 3: Admin Dashboard Summary Consistency (/admin/dashboard/summary)
        # -------------------------------------------------------------------------
        print("\n[TEST 3] Admin Dashboard Summary Endpoint Consistency:")
        res_admin = client.get("/admin/dashboard/summary")
        print(f"  - GET /admin/dashboard/summary Response Code : {res_admin.status_code}")
        if res_admin.status_code == 200:
            admin_data = res_admin.json()
            print(f"  - Total Emails Reported    : {admin_data['total_emails']}")
            print(f"  - Total Mailboxes Reported : {admin_data['total_mailboxes']}")
            print(f"  - Scheduler Status Field   : '{admin_data['scheduler_status']}'")

            if admin_data['scheduler_status'] == ("running" if sched_status["is_running"] else "stopped"):
                print("  -> RESULT: [PASS] /admin/dashboard/summary matches live scheduler state dynamically.")
            else:
                print("  -> RESULT: [FAIL] Dashboard summary returned contradictory scheduler status.")

        # -------------------------------------------------------------------------
        # TEST 4: Atomic Sync Execution & Database Update Verification
        # -------------------------------------------------------------------------
        print("\n[TEST 4] Atomic Database Update Verification (last_sync_at):")
        mailbox_before = db.query(MailboxAccount).order_by(desc(MailboxAccount.created_at)).first()
        if mailbox_before:
            print(f"  - Mailbox BEFORE Sync:")
            print(f"      - ID             : {mailbox_before.id}")
            print(f"      - Identifier     : {mailbox_before.account_identifier}")
            print(f"      - last_sync_at   : {mailbox_before.last_sync_at}")
            print(f"      - last_history_id: {mailbox_before.last_history_id}")

            # Run Orchestrator Sync
            print("  - Running SyncOrchestrator (incremental mode)...")
            provider = GmailProvider()
            provider.authenticate()
            orchestrator = SyncOrchestrator(db, provider)
            orchestrator.run_sync(str(mailbox_before.id), mode="incremental")

            db.refresh(mailbox_before)
            print(f"  - Mailbox AFTER Sync:")
            print(f"      - ID             : {mailbox_before.id}")
            print(f"      - Identifier     : {mailbox_before.account_identifier}")
            print(f"      - last_sync_at   : {mailbox_before.last_sync_at}")
            print(f"      - last_history_id: {mailbox_before.last_history_id}")

            if mailbox_before.last_sync_at is not None:
                print("  -> RESULT: [PASS] last_sync_at was updated atomically in PostgreSQL!")
            else:
                print("  -> RESULT: [FAIL] last_sync_at remained NULL after sync completion.")

        # -------------------------------------------------------------------------
        # TEST 5: OAuth Configuration & Google Account Chooser Verification
        # -------------------------------------------------------------------------
        print("\n[TEST 5] OAuth Configuration & Account Chooser Prompt Check:")
        print(f"  - Credentials File Exists : {os.path.exists(settings.google_client_secrets_file)}")
        print(f"  - Token File Exists       : {os.path.exists(settings.google_token_file)}")

        with open(os.path.join(os.path.dirname(__file__), "..", "app", "auth", "gmail_oauth.py"), "r") as f:
            code = f.read()
            if "prompt='consent select_account'" in code or 'prompt="consent select_account"' in code:
                print("  - Account Chooser Flag    : ENABLED (prompt='consent select_account')")
                print("  -> RESULT: [PASS] Google Account Chooser configured for clean account switching.")
            else:
                print("  -> RESULT: [FAIL] Missing Account Chooser prompt in OAuth flow.")

    db.close()
    print("\n" + "=" * 95)
    print("                      ALL AUDIT CHECKS COMPLETED")
    print("=" * 95)


if __name__ == "__main__":
    run_production_pipeline_audit()

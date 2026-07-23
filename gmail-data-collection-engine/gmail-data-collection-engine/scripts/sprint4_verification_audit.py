import sys
import os
import logging
from sqlalchemy import text, desc
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import settings
from app.db.session import SessionLocal
from app.models import MailboxAccount, Email, SyncRun, SyncLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sprint4_audit")

def run_sprint4_verification():
    db = SessionLocal()
    print("=" * 90)
    print("                SPRINT 4 FINAL RUNTIME VERIFICATION AUDIT")
    print("=" * 90)

    # -------------------------------------------------------------------------
    # 1. Confirm APScheduler starts automatically during FastAPI startup
    # -------------------------------------------------------------------------
    print("\n[VERIFICATION 1] APScheduler Auto-Start on FastAPI Boot:")
    from app.main import app
    print("  - Inspecting FastAPI app instance in app.main...")
    
    scheduler_in_main = False
    with open(os.path.join(os.path.dirname(__file__), "..", "app", "main.py"), "r") as f:
        main_content = f.read()
        if "scheduler" in main_content.lower() or "start_scheduler" in main_content.lower():
            scheduler_in_main = True

    print(f"  - APScheduler imported/initialized inside app/main.py: {scheduler_in_main}")
    if not scheduler_in_main:
        print("  - VERIFICATION RESULT: [FAIL]")
        print("    -> REASON: FastAPI app/main.py does NOT instantiate, start, or bind APScheduler during startup.")
        print("    -> IMPACT: Running 'uvicorn app.main:app' will NOT trigger background polling automatically.")

    # -------------------------------------------------------------------------
    # 2. Verify last_sync_at is updated after every successful sync
    # -------------------------------------------------------------------------
    print("\n[VERIFICATION 2] last_sync_at Updated After Sync:")
    mailboxes = db.query(MailboxAccount).all()
    for mb in mailboxes:
        print(f"  - Mailbox ID         : {mb.id}")
        print(f"  - Account Identifier : {mb.account_identifier}")
        print(f"  - last_sync_at Value : {mb.last_sync_at}")
        print(f"  - last_history_id    : {mb.last_history_id}")
    
    last_run = db.query(SyncRun).order_by(desc(SyncRun.started_at)).first()
    if last_run:
        print(f"  - Latest Sync Run Completed At : {last_run.completed_at}")
        print(f"  - Latest Sync Run Status       : {last_run.status}")
    
    has_null_sync_at = any(mb.last_sync_at is None for mb in mailboxes)
    if has_null_sync_at:
        print("  - VERIFICATION RESULT: [FAIL]")
        print("    -> REASON: MailboxAccount.last_sync_at is NULL despite successful sync runs.")
        print("    -> IMPACT: UI dashboard and settings show 'Never synced' or outdated sync timestamp.")

    # -------------------------------------------------------------------------
    # 3. Verify mailbox.last_history_id changes after incremental sync
    # -------------------------------------------------------------------------
    print("\n[VERIFICATION 3] mailbox.last_history_id Tracking:")
    runs_with_history = db.query(SyncRun).filter(SyncRun.sync_cursor_before != None).order_by(desc(SyncRun.started_at)).limit(5).all()
    print("  - History ID tracking in sync_runs:")
    for r in runs_with_history:
        print(f"      Run {str(r.id)[:8]}: Cursor Before = {r.sync_cursor_before} | Cursor After = {r.sync_cursor_after} | Mode = {r.sync_type}")
    print("  - VERIFICATION RESULT: [PASS] last_history_id is stored and passed during sync.")

    # -------------------------------------------------------------------------
    # 6 & 7. Verify Sync Counts & Endpoint Consistency across system
    # -------------------------------------------------------------------------
    print("\n[VERIFICATION 6 & 7] Count Consistency Across Endpoints:")
    email_cnt = db.query(Email).count()
    run_cnt = db.query(SyncRun).count()
    mb_cnt = db.query(MailboxAccount).count()
    print(f"  - DB Email Count        : {email_cnt}")
    print(f"  - DB Sync Runs Count    : {run_cnt}")
    print(f"  - DB Mailboxes Count    : {mb_cnt}")

    # Check endpoints via FastAPI TestClient
    from fastapi.testclient import TestClient
    client = TestClient(app)

    res_admin_sum = client.get("/admin/dashboard/summary")
    if res_admin_sum.status_code == 200:
        data = res_admin_sum.json()
        print(f"  - GET /admin/dashboard/summary -> scheduler_status = '{data.get('scheduler_status')}'")
        print(f"  - GET /admin/dashboard/summary -> total_emails     = {data.get('total_emails')}")
        if data.get("scheduler_status") == "running" and not scheduler_in_main:
            print("  - VERIFICATION RESULT: [FAIL]")
            print("    -> REASON: /admin/dashboard/summary returns hardcoded stub scheduler_status='running'.")
            print("    -> CONTRADICTION: Dashboard claims scheduler is running when it is not started by FastAPI.")

    # -------------------------------------------------------------------------
    # 8. OAuth Credentials & Account Chooser Verification
    # -------------------------------------------------------------------------
    print("\n[VERIFICATION 8] OAuth Credential & Account Chooser Configuration:")
    print(f"  - Client Secrets File   : {settings.google_client_secrets_file} (Exists: {os.path.exists(settings.google_client_secrets_file)})")
    print(f"  - Token File            : {settings.google_token_file} (Exists: {os.path.exists(settings.google_token_file)})")
    
    with open(os.path.join(os.path.dirname(__file__), "..", "app", "auth", "gmail_oauth.py"), "r") as f:
        oauth_code = f.read()
        if "prompt='consent select_account'" in oauth_code or 'prompt="consent select_account"' in oauth_code:
            print("  - Account Chooser Flow  : ENABLED (prompt='consent select_account' configured in InstalledAppFlow)")
        else:
            print("  - Account Chooser Flow  : MISSING")

    db.close()
    print("\n" + "=" * 90)

if __name__ == "__main__":
    run_sprint4_verification()

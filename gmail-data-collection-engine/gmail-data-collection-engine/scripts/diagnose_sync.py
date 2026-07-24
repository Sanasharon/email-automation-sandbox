"""Quick diagnostic: check mailbox state, emails, sync_runs, sync_errors."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from app.db.session import SessionLocal
from sqlalchemy import text

MAILBOX_ID = "42b1bf39-fab5-40e8-aa8a-cd69b80648ba"

db = SessionLocal()
try:
    # Mailbox state
    r = db.execute(text("SELECT account_identifier, is_active, sync_status, last_sync_at, last_history_id FROM mailbox_accounts WHERE id = :id"), {"id": MAILBOX_ID})
    row = r.fetchone()
    if row:
        print(f"=== MAILBOX: {row[0]} ===")
        print(f"  is_active: {row[1]}")
        print(f"  sync_status: {row[2]}")
        print(f"  last_sync_at: {row[3]}")
        print(f"  last_history_id: {row[4]}")
    else:
        print("MAILBOX NOT FOUND")

    # Email count
    r = db.execute(text("SELECT COUNT(*) FROM emails WHERE mailbox_account_id = :id"), {"id": MAILBOX_ID})
    print(f"\nTotal emails: {r.scalar()}")

    # Recent 5 emails
    r = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'emails' ORDER BY ordinal_position"))
    cols = [row[0] for row in r.fetchall()]
    print(f"\nEmail columns: {', '.join(cols)}")
    
    # Find sender-like column
    sender_col = None
    for c in ['from_address', 'sender_email', 'from_email', 'sender']:
        if c in cols:
            sender_col = c
            break
    
    date_col = 'received_at' if 'received_at' in cols else 'created_at'
    if sender_col:
        r = db.execute(text(f"SELECT subject, {sender_col}, {date_col}, created_at FROM emails WHERE mailbox_account_id = :id ORDER BY created_at DESC LIMIT 5"), {"id": MAILBOX_ID})
    else:
        r = db.execute(text(f"SELECT subject, {date_col}, created_at FROM emails WHERE mailbox_account_id = :id ORDER BY created_at DESC LIMIT 5"), {"id": MAILBOX_ID})
    rows = r.fetchall()
    if rows:
        print("\nRecent emails:")
        for row in rows:
            subj = (row[0] or "(no subject)")[:60]
            info = " | ".join(str(v) for v in row)
            print(f"  {info}")

    # Sync runs
    r = db.execute(text("SELECT COUNT(*) FROM sync_runs WHERE mailbox_account_id = :id"), {"id": MAILBOX_ID})
    print(f"\nSync runs: {r.scalar()}")

    r = db.execute(text("SELECT status, emails_found, emails_inserted, emails_failed, started_at, completed_at FROM sync_runs WHERE mailbox_account_id = :id ORDER BY started_at DESC LIMIT 3"), {"id": MAILBOX_ID})
    rows = r.fetchall()
    if rows:
        for row in rows:
            print(f"  {row[4]} -> {row[5]} | status={row[0]} found={row[1]} inserted={row[2]} failed={row[3]}")

    # Sync errors
    r = db.execute(text("SELECT COUNT(*) FROM sync_errors WHERE mailbox_account_id = :id"), {"id": MAILBOX_ID})
    print(f"\nSync errors: {r.scalar()}")

    r = db.execute(text("SELECT error_type, error_message, created_at FROM sync_errors WHERE mailbox_account_id = :id ORDER BY created_at DESC LIMIT 5"), {"id": MAILBOX_ID})
    rows = r.fetchall()
    if rows:
        for row in rows:
            print(f"  {row[2]} | {row[0]}: {row[1][:80] if row[1] else ''}")

    # Scheduler config check
    from app.config import settings
    print(f"\n=== SCHEDULER CONFIG ===")
    print(f"  scheduler_enabled: {settings.scheduler_enabled}")
    print(f"  sync_interval_minutes: {settings.sync_interval_minutes}")
    print(f"  max_emails_per_sync: {settings.max_emails_per_sync}")

    # Check token file
    import os
    token_path = os.path.join(os.path.dirname(__file__), "..", settings.google_token_file)
    print(f"\n  Token file exists: {os.path.exists(token_path)}")
    if os.path.exists(token_path):
        print(f"  Token file size: {os.path.getsize(token_path)} bytes")

    # Check credentials file
    creds_path = os.path.join(os.path.dirname(__file__), "..", settings.google_client_secrets_file)
    print(f"  Credentials file exists: {os.path.exists(creds_path)}")

finally:
    db.close()

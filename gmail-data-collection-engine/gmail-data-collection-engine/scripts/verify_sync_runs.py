import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.models.sync_run import SyncRun
from sqlalchemy import desc

def verify_sync_run():
    with SessionLocal() as db:
        latest_run = db.query(SyncRun).order_by(desc(SyncRun.created_at)).first()
        if latest_run:
            print(f"ID: {latest_run.id}")
            print(f"Status: {latest_run.status}")
            print(f"Sync Type: {latest_run.sync_type}")
            print(f"History Pages Processed: {latest_run.history_pages_processed}")
            print(f"Incremental Msg IDs Found: {latest_run.incremental_message_ids_found}")
            print(f"Fallback Full Sync Used: {latest_run.fallback_full_sync_used}")
            print(f"Emails Found: {latest_run.emails_found}")
        else:
            print("No runs found")

if __name__ == "__main__":
    verify_sync_run()

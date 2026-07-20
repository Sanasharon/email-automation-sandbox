import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import engine
from sqlalchemy import text

def apply_migration():
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE sync_runs ADD COLUMN IF NOT EXISTS history_pages_processed INTEGER NOT NULL DEFAULT 0;"))
        conn.execute(text("ALTER TABLE sync_runs ADD COLUMN IF NOT EXISTS incremental_message_ids_found INTEGER NOT NULL DEFAULT 0;"))
        conn.commit()
        print("Incremental metrics columns added successfully.")

if __name__ == "__main__":
    apply_migration()

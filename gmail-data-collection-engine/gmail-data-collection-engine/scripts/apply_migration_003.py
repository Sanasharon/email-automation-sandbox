import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import engine
from sqlalchemy import text

def apply_migration():
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE sync_runs DROP CONSTRAINT IF EXISTS ck_sync_run_status;"))
        conn.execute(text("ALTER TABLE sync_runs ADD CONSTRAINT ck_sync_run_status CHECK (status IN ('pending', 'running', 'completed', 'partial_failure', 'failed', 'cancelled'));"))
        conn.commit()
        print("Migration applied successfully.")

if __name__ == "__main__":
    apply_migration()

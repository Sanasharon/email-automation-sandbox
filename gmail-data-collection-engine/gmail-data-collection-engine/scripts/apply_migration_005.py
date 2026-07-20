import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import engine
from sqlalchemy import text

def apply_migration():
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE mailbox_accounts ADD COLUMN IF NOT EXISTS sync_lock_token VARCHAR NULL;"))
        conn.execute(text("ALTER TABLE mailbox_accounts ADD COLUMN IF NOT EXISTS sync_locked_at TIMESTAMP WITH TIME ZONE NULL;"))
        conn.execute(text("ALTER TABLE mailbox_accounts ADD COLUMN IF NOT EXISTS sync_lock_expires_at TIMESTAMP WITH TIME ZONE NULL;"))
        conn.commit()
        print("Mailbox lock columns added successfully.")

if __name__ == "__main__":
    apply_migration()

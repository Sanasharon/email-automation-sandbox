import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.models.mailbox_account import MailboxAccount

def reset_cursor():
    db = SessionLocal()
    try:
        accounts = db.query(MailboxAccount).all()
        for acc in accounts:
            print(f"Resetting last_history_id for {acc.account_identifier} (was {acc.last_history_id})")
            acc.last_history_id = None
        db.commit()
        print("Successfully reset all history cursors. The next sync will be a FULL SYNC.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_cursor()

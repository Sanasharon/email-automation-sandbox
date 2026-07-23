import sys
import os
import logging
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.providers.gmail_provider import GmailProvider
from app.services.mailbox_service import MailboxService
from app.services.sync_orchestrator import SyncOrchestrator
from app.models.email import Email

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("sync_real_gmail")

def main():
    logger.info("=== Purging Stale Test Emails & Starting Real Gmail Sync ===")
    
    db = SessionLocal()
    
    # 1. Delete old dummy test emails (e.g. sender = 'test@example.com')
    try:
        deleted_count = db.execute(text("DELETE FROM emails WHERE sender_email LIKE '%test@example.com%' OR sender_email LIKE '%test%';")).rowcount
        db.commit()
        logger.info(f"✓ Purged {deleted_count} dummy test emails from database.")
    except Exception as e:
        logger.warning(f"Notice on purging test emails: {e}")
        db.rollback()

    # 2. Authenticate Gmail Provider via OAuth
    provider = GmailProvider()
    try:
        provider.authenticate()
        logger.info("✓ OAuth Authentication Successful.")
    except Exception as e:
        logger.error(f"❌ Gmail OAuth Authentication failed: {e}")
        db.close()
        sys.exit(1)

    # 3. Get Account Profile from Google Gmail API
    try:
        profile = provider.get_account_profile()
        email_address = profile.get("emailAddress")
        history_id = str(profile.get("historyId"))
        logger.info(f"✓ Connected Real Gmail Account: {email_address}")
        logger.info(f"✓ Messages Total in Gmail: {profile.get('messagesTotal')}")
    except Exception as e:
        logger.error(f"❌ Failed to fetch Gmail profile: {e}")
        db.close()
        sys.exit(1)

    # 4. Register or Update Mailbox in Database
    mailbox_service = MailboxService(db)
    try:
        account = mailbox_service.register_or_update_mailbox(
            provider="gmail",
            account_identifier=email_address,
            auth_mode="desktop_oauth",
            history_id=None
        )
        logger.info(f"✓ Mailbox Account Registered ID: {account.id}")
    except Exception as e:
        logger.error(f"❌ Database registration failed: {e}")
        db.close()
        sys.exit(1)

    # 5. Run Full Synchronization using SyncOrchestrator
    orchestrator = SyncOrchestrator(db, provider)
    logger.info("🚀 Ingesting Real Gmail Inbox Emails from Google API...")
    orchestrator.run_sync(str(account.id), mode="full")

    # 6. Report Ingested Emails Count
    real_email_count = db.query(Email).count()
    logger.info(f"✅ SUCCESS: Database now contains {real_email_count} REAL Gmail inbox emails!")
    
    db.close()

if __name__ == "__main__":
    main()

import sys
import os
import logging
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.providers.gmail_provider import GmailProvider
from app.services.mailbox_service import MailboxService
from app.services.sync_orchestrator import SyncOrchestrator

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("manual_sync")

def main():
    parser = argparse.ArgumentParser(description="Manual Gmail Sync")
    parser.add_argument("--mode", choices=["full", "incremental"], default="incremental", help="Sync mode")
    args = parser.parse_args()
    mode = args.mode

    logger.info(f"Starting Manual Gmail Sync (mode: {mode})...")
    
    provider = GmailProvider()
    
    try:
        provider.authenticate()
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        sys.exit(1)

    try:
        profile = provider.get_account_profile()
        email_address = profile.get("emailAddress")
        history_id = str(profile.get("historyId"))
    except Exception as e:
        logger.error(f"Failed to fetch Gmail profile: {str(e)}")
        sys.exit(1)

    db = SessionLocal()
    mailbox_service = MailboxService(db)
    
    try:
        account = mailbox_service.register_or_update_mailbox(
            provider="gmail",
            account_identifier=email_address,
            auth_mode="desktop_oauth",
            history_id=None
        )
    except Exception as e:
        logger.error(f"Database registration failed: {str(e)}")
        sys.exit(1)

    account_id = str(account.id)
    
    orchestrator = SyncOrchestrator(db, provider)
    orchestrator.run_sync(account_id, mode=mode)
    
    db.close()

if __name__ == "__main__":
    main()

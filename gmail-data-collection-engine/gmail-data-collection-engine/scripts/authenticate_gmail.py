import sys
import os
import logging

# Add the project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.providers.gmail_provider import GmailProvider
from app.services.mailbox_service import MailboxService

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("authenticate_gmail")

def main():
    logger.info("Starting Gmail Desktop OAuth Authentication...")
    
    provider = GmailProvider()
    
    try:
        provider.authenticate()
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        sys.exit(1)
    try:
        profile = provider.get_account_profile()
        email_address = profile.get("emailAddress")
        history_id = profile.get("historyId")
        if not email_address or not history_id:
            raise ValueError("Profile missing emailAddress or historyId.")
    except Exception as e:
        logger.error(f"Failed to fetch Gmail profile: {str(e)}")
        sys.exit(1)

    # Database Registration
    db = SessionLocal()
    mailbox_service = MailboxService(db)
    
    try:
        account = mailbox_service.register_or_update_mailbox(
            provider="gmail",
            account_identifier=email_address,
            auth_mode="desktop_oauth",
            history_id=str(history_id)
        )
        logger.info(f"Successfully authenticated and connected Gmail account: {account.account_identifier}")
        logger.info(f"Mailbox Account ID: {account.id}")
        logger.info(f"Provider: {account.provider}")
        logger.info(f"Auth Mode: {account.auth_mode}")
        logger.info(f"Current History ID: {account.last_history_id}")
        logger.info(f"Connection Status: {account.sync_status}")
    except Exception as e:
        logger.error(f"Database registration failed: {str(e)}")
        logger.info("OAuth succeeded locally, but mailbox was NOT marked as connected in the database.")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()

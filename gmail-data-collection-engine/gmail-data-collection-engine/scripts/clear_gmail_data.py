"""
Script to clear Gmail account and OAuth tokens for fresh lifecycle testing.
"""
import os
import sys
import json
from pathlib import Path

# Navigate to the parent directory where the app module is located
script_dir = Path(__file__).parent
app_dir = script_dir.parent
sys.path.insert(0, str(app_dir))

from app.db.session import SessionLocal
from app.models.mailbox_account import MailboxAccount
from app.models.workflow import Workflow, WorkflowExecution
from app.models.email import Email
from app.models.attachment import Attachment
from app.models.sync_run import SyncRun
from app.models.sync_log import SyncLog
from app.models.sync_error import SyncError
from app.auth.gmail_oauth import clear_cached_credentials
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_gmail_data():
    """Clear all Gmail-related data from the database."""
    db = SessionLocal()
    try:
        # Delete sync errors first (foreign key dependency)
        sync_error_count = db.query(SyncError).count()
        db.query(SyncError).delete()
        logger.info(f"Deleted {sync_error_count} sync errors")
        
        # Delete sync logs
        sync_log_count = db.query(SyncLog).count()
        db.query(SyncLog).delete()
        logger.info(f"Deleted {sync_log_count} sync logs")
        
        # Delete sync runs
        sync_run_count = db.query(SyncRun).count()
        db.query(SyncRun).delete()
        logger.info(f"Deleted {sync_run_count} sync runs")
        
        # Delete attachments first (foreign key dependency)
        attachment_count = db.query(Attachment).count()
        db.query(Attachment).delete()
        logger.info(f"Deleted {attachment_count} attachments")
        
        # Delete workflow executions
        execution_count = db.query(WorkflowExecution).count()
        db.query(WorkflowExecution).delete()
        logger.info(f"Deleted {execution_count} workflow executions")
        
        # Delete emails
        email_count = db.query(Email).count()
        db.query(Email).delete()
        logger.info(f"Deleted {email_count} emails")
        
        # Delete workflows
        workflow_count = db.query(Workflow).count()
        db.query(Workflow).delete()
        logger.info(f"Deleted {workflow_count} workflows")
        
        # Delete mailbox accounts
        mailbox_count = db.query(MailboxAccount).count()
        db.query(MailboxAccount).delete()
        logger.info(f"Deleted {mailbox_count} mailbox accounts")
        
        db.commit()
        logger.info("Database cleared successfully")
        
        # Clear OAuth tokens
        clear_cached_credentials()
        logger.info("OAuth tokens cleared")
        
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clear Gmail data: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting Gmail data cleanup...")
    success = clear_gmail_data()
    if success:
        logger.info("✓ Gmail data cleared successfully")
        logger.info("✓ OAuth tokens cleared")
        logger.info("Ready for fresh OAuth login")
    else:
        logger.error("✗ Failed to clear Gmail data")
        sys.exit(1)

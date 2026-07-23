"""
Scheduler Job Definitions.
Contains execution logic for scheduled background tasks.
"""
import logging
from app.db.session import SessionLocal
from app.models.mailbox_account import MailboxAccount
from app.models.email import Email
from app.providers.gmail_provider import GmailProvider
from app.services.sync_orchestrator import SyncOrchestrator
from app.services.workflow_execution_service import WorkflowExecutionService

logger = logging.getLogger("scheduler_jobs")


def poll_mailboxes_job():
    """
    Background job triggered by APScheduler.
    Executes incremental Gmail synchronization for all active connected mailboxes
    and evaluates retroactive workflows.
    """
    logger.info("[SCHEDULER_JOB] Starting scheduled incremental mailbox poll...")
    db = SessionLocal()
    try:
        mailboxes = db.query(MailboxAccount).filter(MailboxAccount.sync_status != 'disabled').all()
        logger.info(f"[SCHEDULER_JOB] Found {len(mailboxes)} active mailbox account(s) for polling.")

        for account in mailboxes:
            provider = GmailProvider()
            try:
                provider.authenticate()
                orchestrator = SyncOrchestrator(db, provider)
                orchestrator.run_sync(str(account.id), mode="incremental")
            except Exception as e:
                logger.error(f"[SCHEDULER_JOB] Failed to sync mailbox {account.id}: {e}")

        # --- Retroactive Workflow Execution ---
        try:
            workflow_svc = WorkflowExecutionService(db)
            emails = db.query(Email).all()
            processed_count = 0
            for email in emails:
                workflow_svc.process_email(email)
                processed_count += 1
            db.commit()
            logger.info(f"[SCHEDULER_JOB] Evaluated {processed_count} email(s) against active workflows.")
        except Exception as wf_err:
            logger.error(f"[SCHEDULER_JOB] Failed retroactive workflow execution: {wf_err}")
            db.rollback()

    except Exception as e:
        logger.error(f"[SCHEDULER_JOB] Exception in poll_mailboxes_job: {e}")
    finally:
        db.close()
        logger.info("[SCHEDULER_JOB] Scheduled incremental mailbox poll completed.")

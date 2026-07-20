import sys
import os
import logging
import signal
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED, EVENT_JOB_MAX_INSTANCES

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import settings
from app.db.session import SessionLocal
from app.models.mailbox_account import MailboxAccount
from app.providers.gmail_provider import GmailProvider
from app.services.sync_orchestrator import SyncOrchestrator

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("scheduler")

def poll_mailboxes():
    db = SessionLocal()
    try:
        # We only try to sync accounts that are active (connected or syncing or error)
        # We will let the orchestrator atomic lock handle the rest.
        mailboxes = db.query(MailboxAccount).filter(MailboxAccount.sync_status != 'disabled').all()
        for account in mailboxes:
            provider = GmailProvider()
            try:
                # In a real multi-tenant app, credentials would be loaded per-account.
                # Here we are relying on local desktop oauth file.
                provider.authenticate()
                orchestrator = SyncOrchestrator(db, provider)
                orchestrator.run_sync(str(account.id), mode="incremental")
            except Exception as e:
                logger.error(f"Failed to prepare sync for mailbox {account.id}: {e}")
        
        # --- Retroactive Workflow Execution ---
        # Evaluates existing emails against newly created workflows
        try:
            from app.models.email import Email
            from app.services.workflow_execution_service import WorkflowExecutionService
            workflow_svc = WorkflowExecutionService(db)
            
            emails = db.query(Email).all()
            processed_count = 0
            for email in emails:
                # process_email automatically prevents duplicate executions for the same workflow
                workflow_svc.process_email(email)
                processed_count += 1
            
            db.commit()
            logger.info(f"Retroactively evaluated {processed_count} emails against active workflows.")
        except Exception as e:
            logger.error(f"Failed retroactive workflow execution: {e}")
            db.rollback()
            
    except Exception as e:
        logger.error(f"Failed during mailbox polling: {e}")
    finally:
        db.close()

def job_listener(event):
    if event.code == EVENT_JOB_EXECUTED:
        logger.info(f"Job {event.job_id} executed successfully.")
    elif event.code == EVENT_JOB_ERROR:
        logger.error(f"Job {event.job_id} raised an exception: {event.exception}")
    elif event.code == EVENT_JOB_MISSED:
        logger.warning(f"Job {event.job_id} missed its scheduled execution.")
    elif event.code == EVENT_JOB_MAX_INSTANCES:
        logger.warning(f"Job {event.job_id} reached its maximum allowed instances.")

def main():
    if not settings.scheduler_enabled:
        logger.error("SCHEDULER_ENABLED is false. Exiting.")
        sys.exit(1)

    logger.info("scheduler started")
    
    scheduler = BlockingScheduler(timezone=settings.scheduler_timezone)
    
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED | EVENT_JOB_MAX_INSTANCES)
    
    scheduler.add_job(
        poll_mailboxes,
        'interval',
        seconds=15,
        id='gmail_incremental_poll',
        max_instances=settings.max_sync_instances,
        coalesce=True,
        misfire_grace_time=settings.sync_misfire_grace_seconds,
        replace_existing=True
    )

    def handle_shutdown(signum, frame):
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        scheduler.shutdown(wait=True)
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    main()

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.mailbox_account import MailboxAccount
from app.models.email import Email
from app.models.workflow import Workflow
from app.auth.dependencies import get_current_user
from app.services.mailbox_service import MailboxService
from app.services.sync_orchestrator import SyncOrchestrator
from app.providers.gmail_provider import GmailProvider
from app.auth.gmail_oauth import clear_cached_credentials, NonInteractiveAuthRequired
from app.api.v1.events import broadcast_event
from app.services.system_logger import log_sync_event, log_oauth_event
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mailboxes", tags=["mailboxes"], dependencies=[Depends(get_current_user)])

@router.get("/")
def list_mailboxes(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    service = MailboxService(db)
    accounts = service.get_mailboxes_for_user(current_user["id"])
    result = []
    for acc in accounts:
        email_count = db.query(func.count(Email.id)).filter(Email.mailbox_account_id == acc.id).scalar() or 0
        result.append({
            "id": str(acc.id),
            "provider": acc.provider,
            "account_identifier": acc.account_identifier,
            "email_address": acc.account_identifier,
            "auth_mode": acc.auth_mode,
            "sync_status": acc.sync_status,
            "last_history_id": acc.last_history_id,
            "last_sync_at": acc.last_sync_at.isoformat() if acc.last_sync_at else None,
            "user_id": str(acc.user_id) if acc.user_id else None,
            "email_count": email_count
        })
    return result

@router.post("/connect")
def connect_mailbox(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Initiates Gmail OAuth connection and registers mailbox for current_user."""
    try:
        provider = GmailProvider()
        provider.authenticate()
        profile = provider.get_account_profile()
        email_address = profile.get("emailAddress", "connected_user@gmail.com")
        history_id = str(profile.get("historyId", ""))
        
        service = MailboxService(db)
        account = service.register_or_update_mailbox(
            provider="gmail",
            account_identifier=email_address,
            auth_mode="desktop_oauth",
            history_id=history_id,
            user_id=current_user["id"]
        )
        log_sync_event("info", f"Gmail connected: {email_address}", mailbox_id=str(account.id), user_id=current_user["id"])
        return {
            "success": True,
            "message": f"Successfully connected {email_address}",
            "mailbox": {
                "id": str(account.id),
                "account_identifier": account.account_identifier,
                "sync_status": account.sync_status,
                "last_history_id": account.last_history_id
            }
        }
    except Exception as e:
        logger.error(f"Failed to connect Gmail mailbox: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect Gmail account: {str(e)}")

@router.post("/{mailbox_id}/sync")
def sync_mailbox(mailbox_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    account = db.query(MailboxAccount).filter(MailboxAccount.id == mailbox_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Mailbox account not found")
        
    try:
        provider = GmailProvider()
        try:
            provider.authenticate(interactive=False)
        except NonInteractiveAuthRequired:
            raise HTTPException(
                status_code=401, 
                detail="OAuth credentials missing or expired. Please reconnect your Gmail account first."
            )
        orchestrator = SyncOrchestrator(db, provider)
        success = orchestrator.run_sync(mailbox_id, mode="incremental")
        if success:
            return {"status": "success", "message": "Synchronization completed successfully"}
        raise HTTPException(status_code=400, detail="Sync failed or mailbox is locked")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{mailbox_id}/disconnect")
def disconnect_mailbox(mailbox_id: str, delete_data: bool = False, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Full disconnect lifecycle:
    1. Set mailbox sync_status='disconnected', is_active=False
    2. Pause all associated workflows
    3. Clear OAuth tokens
    4. Optionally delete all synced emails, attachments, sync history
    5. Broadcast mailbox_disconnected event
    """
    account = db.query(MailboxAccount).filter(MailboxAccount.id == mailbox_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Mailbox account not found")
    
    try:
        # 1. Update mailbox status
        account.sync_status = "disconnected"
        account.is_active = False
        db.commit()
        
        # 2. Pause all workflows associated with this mailbox
        workflows = db.query(Workflow).filter(Workflow.mailbox_account_id == mailbox_id).all()
        for workflow in workflows:
            workflow.is_active = False
        db.commit()
        
        # 3. Clear OAuth tokens
        clear_cached_credentials()
        log_oauth_event("info", f"OAuth tokens cleared for mailbox {account.account_identifier}", mailbox_id=mailbox_id)
        
        # 4. Optionally delete all synced data
        deleted_counts = {}
        if delete_data:
            from app.models.attachment import Attachment
            from app.models.sync_run import SyncRun
            from app.models.sync_log import SyncLog
            from app.models.sync_error import SyncError
            from app.models.ai_approval import AIApproval
            
            email_ids = [str(e.id) for e in db.query(Email.id).filter(Email.mailbox_account_id == mailbox_id).all()]
            
            if email_ids:
                db.query(Attachment).filter(Attachment.email_id.in_(email_ids)).delete(synchronize_session=False)
                deleted_counts['attachments'] = len(email_ids)
                
                db.query(AIApproval).filter(AIApproval.email_id.in_(email_ids)).delete(synchronize_session=False)
                deleted_counts['ai_approvals'] = len(email_ids)
            
            email_count = db.query(Email).filter(Email.mailbox_account_id == mailbox_id).delete(synchronize_session=False)
            deleted_counts['emails'] = email_count
            
            sync_count = db.query(SyncRun).filter(SyncRun.mailbox_account_id == mailbox_id).delete(synchronize_session=False)
            deleted_counts['sync_runs'] = sync_count
            
            db.query(SyncLog).filter(SyncLog.sync_run_id.in_(
                db.query(SyncRun.id).filter(SyncRun.mailbox_account_id == mailbox_id)
            )).delete(synchronize_session=False)
            
            db.query(SyncError).filter(SyncError.sync_run_id.in_(
                db.query(SyncRun.id).filter(SyncRun.mailbox_account_id == mailbox_id)
            )).delete(synchronize_session=False)
            
            db.delete(account)
            deleted_counts['mailbox'] = 1
            
            logger.info(f"Deleted all data for mailbox {mailbox_id}: {deleted_counts}")
        
        db.commit()
        
        # 5. Broadcast disconnect event via SSE
        broadcast_event("disconnect", {
            "type": "disconnect",
            "mailbox_id": mailbox_id,
            "status": "disconnected",
            "data_deleted": delete_data
        })
        
        logger.info(f"Mailbox {mailbox_id} fully disconnected. Workflows paused, OAuth cleared.")
        
        return {
            "success": True, 
            "message": "Mailbox disconnected successfully",
            "workflows_paused": len(workflows),
            "data_deleted": delete_data,
            "deleted_counts": deleted_counts if delete_data else None
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to disconnect mailbox {mailbox_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to disconnect mailbox: {str(e)}")

@router.get("/status")
def get_mailbox_status(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns the current mailbox connection status.
    This is the single source of truth for the frontend.
    """
    service = MailboxService(db)
    accounts = service.get_mailboxes_for_user(current_user["id"])
    
    if not accounts:
        return {
            "connected": False,
            "sync_status": "disconnected",
            "mailbox": None
        }
    
    active_account = accounts[0]
    is_connected = active_account.sync_status in ("connected", "syncing")
    
    return {
        "connected": is_connected,
        "sync_status": active_account.sync_status,
        "mailbox": {
            "id": str(active_account.id),
            "account_identifier": active_account.account_identifier,
            "sync_status": active_account.sync_status,
            "last_sync_at": active_account.last_sync_at.isoformat() if active_account.last_sync_at else None,
            "gmail_address": active_account.account_identifier
        }
    }

@router.post("/{mailbox_id}/reconnect")
def reconnect_mailbox(mailbox_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    account = db.query(MailboxAccount).filter(MailboxAccount.id == mailbox_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Mailbox account not found")
    try:
        provider = GmailProvider()
        provider.authenticate()
        profile = provider.get_account_profile()
        account.sync_status = "connected"
        if profile.get("historyId"):
            account.last_history_id = str(profile.get("historyId"))
        db.commit()
        return {"success": True, "message": "Mailbox re-connected successfully"}
    except Exception as e:
        logger.error(f"Failed to reconnect mailbox: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/switch-account")
def switch_mailbox_account(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Clears cached OAuth tokens, disables existing active mailbox, forces Google Account Chooser,
    registers the newly selected Gmail account, and triggers an initial full sync.
    """
    try:
        # 1. Clear cached token file to force Account Chooser prompt
        clear_cached_credentials()

        # 2. Disable existing connected mailboxes for this user
        user_mailboxes = db.query(MailboxAccount).filter(MailboxAccount.user_id == current_user["id"]).all()
        for mb in user_mailboxes:
            mb.sync_status = "disabled"
        db.commit()

        # 3. Trigger new Google OAuth with prompt='consent select_account'
        provider = GmailProvider()
        provider.authenticate()
        profile = provider.get_account_profile()

        email_address = profile.get("emailAddress")
        history_id = str(profile.get("historyId", ""))

        service = MailboxService(db)
        account = service.register_or_update_mailbox(
            provider="gmail",
            account_identifier=email_address,
            auth_mode="desktop_oauth",
            history_id=history_id,
            user_id=current_user["id"]
        )

        # 4. Trigger initial full sync for newly connected account
        orchestrator = SyncOrchestrator(db, provider)
        orchestrator.run_sync(str(account.id), mode="full")

        return {
            "success": True,
            "message": f"Successfully switched account to {email_address} and ran full sync.",
            "mailbox": {
                "id": str(account.id),
                "account_identifier": account.account_identifier,
                "sync_status": account.sync_status,
                "last_history_id": account.last_history_id
            }
        }
    except Exception as e:
        logger.error(f"Failed to switch Gmail account: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to switch account: {str(e)}")

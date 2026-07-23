from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.mailbox_account import MailboxAccount
from app.models.email import Email
from app.auth.dependencies import get_current_user
from app.services.mailbox_service import MailboxService
from app.services.sync_orchestrator import SyncOrchestrator
from app.providers.gmail_provider import GmailProvider
from app.auth.gmail_oauth import clear_cached_credentials
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
        provider.authenticate()
        orchestrator = SyncOrchestrator(db, provider)
        success = orchestrator.run_sync(mailbox_id, mode="incremental")
        if success:
            return {"status": "success", "message": "Synchronization completed successfully"}
        raise HTTPException(status_code=400, detail="Sync failed or mailbox is locked")
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{mailbox_id}/disconnect")
def disconnect_mailbox(mailbox_id: str, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    account = db.query(MailboxAccount).filter(MailboxAccount.id == mailbox_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Mailbox account not found")
    account.sync_status = "disabled"
    db.commit()
    return {"success": True, "message": "Mailbox disconnected successfully"}

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

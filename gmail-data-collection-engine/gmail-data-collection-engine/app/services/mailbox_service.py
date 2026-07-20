from sqlalchemy.orm import Session
from app.models import MailboxAccount

class MailboxService:
    def __init__(self, db: Session):
        self.db = db

    def register_or_update_mailbox(self, provider: str, account_identifier: str, auth_mode: str, history_id: str) -> MailboxAccount:
        """
        Safely registers or updates a mailbox account.
        Returns the MailboxAccount instance if successful.
        Raises an exception if database registration fails.
        """
        account = self.db.query(MailboxAccount).filter(
            MailboxAccount.provider.ilike(provider),
            MailboxAccount.account_identifier.ilike(account_identifier)
        ).first()

        if not account:
            account = MailboxAccount(
                provider=provider.lower(),
                account_identifier=account_identifier.lower(),
                auth_mode=auth_mode,
                sync_status="connected",
                last_history_id=history_id
            )
            self.db.add(account)
        else:
            account.auth_mode = auth_mode
            account.sync_status = "connected"
            if history_id:
                account.last_history_id = history_id

        self.db.commit()
        self.db.refresh(account)
        return account

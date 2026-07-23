from sqlalchemy.orm import Session
from app.models import MailboxAccount

class MailboxService:
    def __init__(self, db: Session):
        self.db = db

    def register_or_update_mailbox(self, provider: str, account_identifier: str, auth_mode: str, history_id: str, user_id: str = None) -> MailboxAccount:
        """
        Safely registers or updates a mailbox account associated with a user.
        Returns the MailboxAccount instance if successful.
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
                last_history_id=history_id,
                user_id=user_id
            )
            self.db.add(account)
        else:
            account.auth_mode = auth_mode
            account.sync_status = "connected"
            if user_id and not account.user_id:
                account.user_id = user_id
            if history_id:
                account.last_history_id = history_id

        self.db.commit()
        self.db.refresh(account)
        return account

    def get_mailboxes_for_user(self, user_id: str = None):
        """Fetches all mailbox accounts owned by the specified user."""
        query = self.db.query(MailboxAccount)
        if user_id:
            query = query.filter(
                (MailboxAccount.user_id == user_id) | (MailboxAccount.user_id == None)
            )
        return query.all()

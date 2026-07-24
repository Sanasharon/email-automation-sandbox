from sqlalchemy import Column, String, Boolean, DateTime, text, Index, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class MailboxAccount(Base):
    __tablename__ = "mailbox_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    provider = Column(String, nullable=False, server_default="gmail")
    account_identifier = Column(String, nullable=False)
    auth_mode = Column(String, nullable=False, server_default="desktop_oauth")
    last_history_id = Column(String, nullable=True)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    sync_status = Column(String, nullable=False, server_default="connected")
    sync_lock_token = Column(String, nullable=True)
    sync_locked_at = Column(DateTime(timezone=True), nullable=True)
    sync_lock_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    # Relationships
    user = relationship("User", backref="mailbox_accounts")
    emails = relationship("Email", back_populates="mailbox_account", passive_deletes=True)
    sync_runs = relationship("SyncRun", back_populates="mailbox_account", passive_deletes=True)

    __table_args__ = (
        Index('uq_mailbox_provider_account_identifier', text('lower(provider)'), text('lower(account_identifier)'), unique=True),
        CheckConstraint("sync_status IN ('connected', 'syncing', 'idle', 'error', 'disabled', 'disconnected', 'oauth_failed')", name="ck_mailbox_account_sync_status"),
    )

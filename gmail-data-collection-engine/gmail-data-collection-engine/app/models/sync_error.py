from sqlalchemy import Column, String, DateTime, text, Index, CheckConstraint, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class SyncError(Base):
    __tablename__ = "sync_errors"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    sync_run_id = Column(UUID(as_uuid=True), ForeignKey("sync_runs.id", ondelete="RESTRICT"), nullable=False)
    gmail_message_id = Column(String, nullable=True)
    mailbox_account_id = Column(UUID(as_uuid=True), ForeignKey("mailbox_accounts.id", ondelete="SET NULL"), nullable=True)
    api_endpoint = Column(String, nullable=True)
    provider_attachment_id = Column(String, nullable=True)
    error_type = Column(String, nullable=False)
    error_message = Column(String, nullable=False)
    error_stack = Column(String, nullable=True)
    retry_count = Column(Integer, nullable=False, server_default="0")
    is_retryable = Column(Boolean, nullable=False, server_default=text("false"))
    resolved = Column(Boolean, nullable=False, server_default=text("false"))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    sync_run = relationship("SyncRun", back_populates="sync_errors")
    mailbox_account = relationship("MailboxAccount")

    __table_args__ = (
        Index('ix_sync_error_sync_run_id', 'sync_run_id'),
        CheckConstraint("retry_count >= 0", name="ck_sync_error_retry_count"),
    )

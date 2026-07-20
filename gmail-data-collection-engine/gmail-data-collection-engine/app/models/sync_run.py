from sqlalchemy import Column, String, DateTime, text, Index, CheckConstraint, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class SyncRun(Base):
    __tablename__ = "sync_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    mailbox_account_id = Column(UUID(as_uuid=True), ForeignKey("mailbox_accounts.id", ondelete="RESTRICT"), nullable=False)
    sync_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    sync_duration_seconds = Column(Integer, nullable=True)
    
    emails_found = Column(Integer, nullable=False, server_default="0")
    emails_processed = Column(Integer, nullable=False, server_default="0")
    emails_inserted = Column(Integer, nullable=False, server_default="0")
    emails_failed = Column(Integer, nullable=False, server_default="0")
    duplicates_skipped = Column(Integer, nullable=False, server_default="0")
    attachments_found = Column(Integer, nullable=False, server_default="0")
    attachments_uploaded = Column(Integer, nullable=False, server_default="0")
    attachments_failed = Column(Integer, nullable=False, server_default="0")
    api_request_count = Column(Integer, nullable=False, server_default="0")
    error_count = Column(Integer, nullable=False, server_default="0")
    
    sync_cursor_before = Column(String, nullable=True)
    sync_cursor_after = Column(String, nullable=True)
    fallback_full_sync_used = Column(Boolean, nullable=False, server_default=text("false"))
    history_pages_processed = Column(Integer, nullable=False, server_default="0")
    incremental_message_ids_found = Column(Integer, nullable=False, server_default="0")
    error_summary = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    mailbox_account = relationship("MailboxAccount", back_populates="sync_runs")
    sync_logs = relationship("SyncLog", back_populates="sync_run", passive_deletes=True)
    sync_errors = relationship("SyncError", back_populates="sync_run", passive_deletes=True)

    __table_args__ = (
        Index('ix_sync_run_mailbox_account_id', 'mailbox_account_id'),
        CheckConstraint("sync_type IN ('full', 'incremental')", name="ck_sync_run_type"),
        CheckConstraint("status IN ('pending', 'running', 'completed', 'partial_failure', 'failed', 'cancelled')", name="ck_sync_run_status"),
        CheckConstraint("sync_duration_seconds >= 0", name="ck_sync_run_duration"),
        CheckConstraint("completed_at IS NULL OR completed_at >= started_at", name="ck_sync_run_completed_at"),
        CheckConstraint("emails_found >= 0", name="ck_sync_run_emails_found"),
        CheckConstraint("emails_processed >= 0", name="ck_sync_run_emails_processed"),
        CheckConstraint("emails_inserted >= 0", name="ck_sync_run_emails_inserted"),
        CheckConstraint("emails_failed >= 0", name="ck_sync_run_emails_failed"),
        CheckConstraint("duplicates_skipped >= 0", name="ck_sync_run_duplicates_skipped"),
        CheckConstraint("attachments_found >= 0", name="ck_sync_run_attachments_found"),
        CheckConstraint("attachments_uploaded >= 0", name="ck_sync_run_attachments_uploaded"),
        CheckConstraint("attachments_failed >= 0", name="ck_sync_run_attachments_failed"),
        CheckConstraint("api_request_count >= 0", name="ck_sync_run_api_request_count"),
        CheckConstraint("error_count >= 0", name="ck_sync_run_error_count"),
    )

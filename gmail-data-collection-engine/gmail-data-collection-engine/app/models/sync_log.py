from sqlalchemy import Column, String, DateTime, text, Index, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base

class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    sync_run_id = Column(UUID(as_uuid=True), ForeignKey("sync_runs.id", ondelete="RESTRICT"), nullable=False)
    level = Column(String, nullable=False)
    message = Column(String, nullable=False)
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    sync_run = relationship("SyncRun", back_populates="sync_logs")

    __table_args__ = (
        Index('ix_sync_log_sync_run_id', 'sync_run_id'),
        CheckConstraint("level IN ('info', 'warning', 'error', 'debug')", name="ck_sync_log_level"),
    )

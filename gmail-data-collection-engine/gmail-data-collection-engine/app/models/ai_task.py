# app/models/ai_task.py
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from app.db.base import Base

class AiTask(Base):
    __tablename__ = "ai_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    email_id = Column(UUID(as_uuid=True), ForeignKey("emails.id", ondelete="CASCADE"), nullable=True)
    task_type = Column(String(50), nullable=False)  # e.g. 'classification' | 'priority'
    payload = Column(JSONB, nullable=True)          # optional task-specific data
    status = Column(String(20), nullable=False, server_default=text("'pending'"))  # pending|processing|completed|failed
    result = Column(JSONB, nullable=True)           # JSON result written by worker
    error = Column(Text, nullable=True)             # error message if failed
    attempts = Column(Integer, nullable=False, server_default=text("0"))
    max_attempts = Column(Integer, nullable=False, server_default=text("3"))
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    # optional relationship back to Email for convenient access in code
    email = relationship("Email", back_populates="ai_tasks")
from sqlalchemy import Column, String, DateTime, Text, text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    level = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSONB, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    user = relationship("User")

    __table_args__ = (
        Index('ix_system_logs_level', 'level'),
        Index('ix_system_logs_category', 'category'),
        Index('ix_system_logs_created_at', 'created_at', postgresql_using='btree', postgresql_ops={'created_at': 'DESC'}),
    )

from sqlalchemy import Column, String, DateTime, text, Index, CheckConstraint, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    email_id = Column(UUID(as_uuid=True), ForeignKey("emails.id", ondelete="RESTRICT"), nullable=False)
    provider_attachment_id = Column(String, nullable=True)
    provider_part_id = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    storage_bucket = Column(String, nullable=False, server_default="email-attachments")
    storage_path = Column(String, nullable=True)
    download_status = Column(String, nullable=False, server_default="pending")
    upload_error = Column(String, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    email = relationship("Email", back_populates="attachments")

    __table_args__ = (
        Index('uq_attachment_email_provider_att_id', 'email_id', 'provider_attachment_id', unique=True, postgresql_where=text("provider_attachment_id IS NOT NULL")),
        Index('uq_attachment_email_provider_part_id', 'email_id', 'provider_part_id', unique=True, postgresql_where=text("provider_part_id IS NOT NULL")),
        Index('ix_attachment_email_id', 'email_id'),
        CheckConstraint("provider_attachment_id IS NOT NULL OR provider_part_id IS NOT NULL", name="ck_attachment_identity"),
        CheckConstraint("size_bytes >= 0", name="ck_attachment_size_bytes"),
        CheckConstraint("download_status IN ('pending', 'downloading', 'uploaded', 'failed')", name="ck_attachment_download_status"),
    )

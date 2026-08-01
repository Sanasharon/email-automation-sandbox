# app/models/email_category.py
from sqlalchemy import Column, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from app.db.base import Base

class EmailCategory(Base):
    __tablename__ = "email_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    email_id = Column(UUID(as_uuid=True), ForeignKey("emails.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    confidence = Column(Float, nullable=False, server_default=text("0.0"))
    assigned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    corrected = Column(Boolean, nullable=False, server_default=text("false"))

    # relationships
    email = relationship("Email", back_populates="category_associations")
    category = relationship("Category", back_populates="email_associations")
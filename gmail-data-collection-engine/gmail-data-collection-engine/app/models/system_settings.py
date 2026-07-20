from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True)
    value_json = Column(JSONB, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

# app/schemas/email.py
from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime
from app.schemas.category import EmailCategoryResponse

class EmailListItem(BaseModel):
    id: UUID4
    sender_email: Optional[str]
    subject: Optional[str]
    labels: List[str]
    category: Optional[str] = None
    processing_status: str
    received_at: Optional[datetime]
    provider_message_id: Optional[str] = None
    provider_thread_id: Optional[str] = None
    retry_count: int = 0
    workflow_execution_id: Optional[str] = None
    last_processing_error: Optional[str] = None

    workflow_name: Optional[str] = None
    last_action: Optional[str] = None
    workflow_status: Optional[str] = None
    processing_duration: Optional[float] = None
    has_attachments: bool = False

    # NEW: priority fields
    priority: Optional[str] = "Medium"
    priority_confidence: Optional[float] = 0.0

    # NEW: include category associations
    categories: List[EmailCategoryResponse] = []

    class Config:
        from_attributes = True

class PaginatedEmailResponse(BaseModel):
    data: List[EmailListItem]
    total: int
    page: int
    page_size: int

class AttachmentSchema(BaseModel):
    id: UUID4
    filename: str
    mime_type: str
    size_bytes: int

    class Config:
        from_attributes = True

class EmailDetailResponse(EmailListItem):
    to_recipients: List[str]
    cc_recipients: List[str]
    bcc_recipients: List[str]
    body_text: Optional[str]
    body_html: Optional[str]
    attachments: List[AttachmentSchema] = []
    execution_timeline: List[dict] = []
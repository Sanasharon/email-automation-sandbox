from pydantic import BaseModel, UUID4, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class DashboardSummaryResponse(BaseModel):
    total_mailboxes: int
    total_emails: int
    total_attachments: int
    total_sync_runs: int
    successful_syncs: int
    failed_syncs: int
    last_sync_time: Optional[datetime]
    scheduler_status: str

    model_config = ConfigDict(from_attributes=True)

class MailboxAdminResponse(BaseModel):
    id: UUID4
    email_address: str
    sync_mode: str
    history_id: Optional[str]
    last_sync_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EmailAdminListResponse(BaseModel):
    id: UUID4
    sender_email: Optional[str]
    to_recipients: List[Any]
    subject: Optional[str]
    labels: List[Any]
    received_at: Optional[datetime]
    has_attachments: bool

    model_config = ConfigDict(from_attributes=True)

class AttachmentMinimalResponse(BaseModel):
    id: UUID4
    file_name: Optional[str]
    mime_type: Optional[str]
    size_bytes: Optional[int]

    model_config = ConfigDict(from_attributes=True)

class EmailAdminDetailResponse(BaseModel):
    id: UUID4
    sender_email: Optional[str]
    to_recipients: List[Any]
    subject: Optional[str]
    labels: List[Any]
    received_at: Optional[datetime]
    has_attachments: bool
    body_preview: Optional[str]
    thread_id: Optional[str]
    related_attachments: List[AttachmentMinimalResponse]

    model_config = ConfigDict(from_attributes=True)

class AttachmentAdminResponse(BaseModel):
    id: UUID4
    file_name: Optional[str]
    mime_type: Optional[str]
    size_bytes: Optional[int]
    parent_email_subject: Optional[str]
    sender_email: Optional[str]
    storage_path: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DownloadUrlResponse(BaseModel):
    url: str

class SyncRunAdminResponse(BaseModel):
    sync_run_id: UUID4
    sync_type: str
    status: str
    emails_found: int
    emails_inserted: int
    duplicates_skipped: int
    emails_failed: int
    attachments_uploaded: int
    started_at: datetime
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class SyncLogAdminResponse(BaseModel):
    id: UUID4
    level: str
    message: str
    metadata_json: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SyncErrorAdminResponse(BaseModel):
    error_type: str
    error_message: str
    created_at: datetime
    sync_run_id: UUID4

    model_config = ConfigDict(from_attributes=True)

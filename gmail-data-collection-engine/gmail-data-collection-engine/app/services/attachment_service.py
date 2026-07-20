from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Attachment
import logging

logger = logging.getLogger(__name__)

class AttachmentService:
    def __init__(self, db: Session):
        self.db = db

    def attachment_exists(self, email_id: str, provider_attachment_id: str) -> bool:
        exists = self.db.query(Attachment.id).filter(
            Attachment.email_id == email_id,
            Attachment.provider_attachment_id == provider_attachment_id
        ).first()
        return bool(exists)

    def save_attachment(self, email_id: str, provider_attachment_id: str, filename: str, mime_type: str, size: int, storage_bucket: str, storage_path: str) -> Attachment:
        attachment = Attachment(
            email_id=email_id,
            provider_attachment_id=provider_attachment_id,
            file_name=filename,
            mime_type=mime_type,
            size_bytes=size,
            storage_bucket=storage_bucket,
            storage_path=storage_path,
            download_status="uploaded"
        )
        try:
            self.db.add(attachment)
            self.db.flush()
            return attachment
        except Exception as e:
            self.db.rollback()
            if isinstance(e, IntegrityError) and ("uq_attachment" in str(e) or "duplicate key" in str(e)):
                return None
            raise e

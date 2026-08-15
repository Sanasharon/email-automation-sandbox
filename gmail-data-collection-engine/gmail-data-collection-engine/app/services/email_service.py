from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Email
from app.utils.sanitize_gmail_payload import sanitize_gmail_payload
from app.services.ai_task_service import enqueue_task
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, db: Session):
        self.db = db

    def save_email(self, mailbox_account_id: str, parsed_data: dict) -> tuple[bool, Email]:
        """
        Saves an email to the database safely.
        Returns (inserted: bool, email: Email).
        """
        exists = self.db.query(Email.id).filter(
            Email.mailbox_account_id == mailbox_account_id,
            Email.provider_message_id == parsed_data["provider_message_id"]
        ).first()

        if exists:
            return False, None

        ALLOWED_KEYS = {
            "provider_message_id", "provider_thread_id", "sender_email",
            "to_recipients", "cc_recipients", "bcc_recipients", "subject",
            "received_at", "is_read", "has_attachments", "body_text",
            "body_html", "snippet", "labels", "raw_email_json"
        }

        # Reject unknown fields safely
        unknown_fields = [k for k in parsed_data.keys() if k not in ALLOWED_KEYS]
        if unknown_fields:
            logger.warning(f"Stripping unknown fields before insert: {unknown_fields}")

        required = ["provider_message_id"]
        missing = [f for f in required if not parsed_data.get(f)]
        if missing:
            logger.error(f"Missing required fields: {missing}")
            raise ValueError(f"Missing required fields: {missing}")

        sanitized_json = sanitize_gmail_payload(parsed_data.get("raw_email_json", {}))

        # Combine text content for fast immediate heuristic classification
        text_parts = []
        if parsed_data.get("subject"):
            text_parts.append(parsed_data["subject"])
        if parsed_data.get("body_text"):
            text_parts.append(parsed_data["body_text"])
        if parsed_data.get("snippet"):
            text_parts.append(parsed_data["snippet"])
        content_str = "\n\n".join(text_parts)

        # 1. Instant heuristic category
        from app.services.classification_service import _fallback_keyword_classify
        initial_categories = _fallback_keyword_classify(content_str)
        initial_category = initial_categories[0]["category"] if initial_categories else "General"

        # 2. Instant heuristic priority
        from app.services.priority_service import _heuristic_priority
        initial_priority_dict = _heuristic_priority(content_str, sender_email=parsed_data.get("sender_email"))
        initial_priority = initial_priority_dict.get("priority", "Medium")
        initial_confidence = float(initial_priority_dict.get("confidence", 0.5))

        email = Email(
            mailbox_account_id=mailbox_account_id,
            provider_message_id=parsed_data["provider_message_id"],
            provider_thread_id=parsed_data.get("provider_thread_id"),
            sender_email=parsed_data.get("sender_email"),
            to_recipients=parsed_data.get("to_recipients", []),
            cc_recipients=parsed_data.get("cc_recipients", []),
            bcc_recipients=parsed_data.get("bcc_recipients", []),
            subject=parsed_data.get("subject"),
            snippet=parsed_data.get("snippet"),
            labels=parsed_data.get("labels", []),
            received_at=parsed_data.get("received_at"),
            is_read=parsed_data.get("is_read", True),
            has_attachments=parsed_data.get("has_attachments", False),
            body_text=parsed_data.get("body_text"),
            body_html=parsed_data.get("body_html"),
            raw_email_json=sanitized_json,
            category=initial_category,
            priority=initial_priority,
            priority_confidence=initial_confidence,
            processing_status="collected",
            ai_processing_status="not_started",
            record_status="active"
        )

        try:
            self.db.add(email)
            self.db.commit()
            self.db.refresh(email)
            logger.info(f"[EMAIL_SAVED] Saved email {parsed_data['provider_message_id']} for mailbox {mailbox_account_id}")

            # Broadcast real-time ingestion & badge events immediately to frontend
            try:
                from app.api.v1.events import broadcast_event
                email_payload = {
                    "id": str(email.id),
                    "mailbox_account_id": str(mailbox_account_id),
                    "sender_email": email.sender_email,
                    "sender": email.sender_email,
                    "subject": email.subject,
                    "category": email.category,
                    "priority": email.priority,
                    "priority_confidence": email.priority_confidence,
                    "status": "collected",
                    "received_at": email.received_at.isoformat() if email.received_at else None,
                    "sent_time": email.received_at.isoformat() if email.received_at else None,
                    "has_attachments": email.has_attachments
                }
                broadcast_event("email_saved", {"email": email_payload, "mailbox_id": str(mailbox_account_id)})
                broadcast_event("badge_updated", {
                    "email_id": str(email.id),
                    "mailbox_id": str(mailbox_account_id),
                    "category": email.category,
                    "priority": email.priority,
                    "priority_confidence": email.priority_confidence,
                    "status": email.processing_status
                })
            except Exception as b_err:
                logger.warning(f"[SSE] Non-fatal broadcast error on email_saved: {b_err}")

            # Queue this email for AI classification + priority scoring refinement.
            try:
                enqueue_task(self.db, task_type="classification", email_id=str(email.id))
                enqueue_task(self.db, task_type="priority", email_id=str(email.id))
            except Exception as enqueue_err:
                logger.error(f"[AI_TASK_ENQUEUE_FAILED] email={email.id}: {enqueue_err}")

            return True, email
        except Exception as e:
            self.db.rollback()
            if isinstance(e, IntegrityError) or "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                logger.info(f"[EMAIL_DUPLICATE] Duplicate email {parsed_data.get('provider_message_id')} skipped")
                return False, None
            logger.error(f"[EMAIL_ERROR] Failed to save email {parsed_data.get('provider_message_id')}: {e}")
            raise e
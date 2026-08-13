from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Email, MailboxAccount
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

        sanitized_json = sanitize_gmail_payload(
            parsed_data.get("raw_email_json", {})
        )

        mailbox = self.db.query(MailboxAccount).filter(
            MailboxAccount.id == mailbox_account_id
        ).first()

        if not mailbox:
            raise ValueError(f"Mailbox account not found: {mailbox_account_id}")

        company_id_val = mailbox.company_id

        if not company_id_val:
            raise ValueError(
                f"company_id not found for mailbox: {mailbox_account_id}"
            )

        email = Email(
            mailbox_account_id=mailbox_account_id,
            company_id=company_id_val,
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
            processing_status="collected",
            ai_processing_status="not_started",
            record_status="active"
        )

        try:
            self.db.add(email)
            self.db.commit()
            self.db.refresh(email)
            logger.info(
                f"[EMAIL_SAVED] Saved email {parsed_data['provider_message_id']} "
                f"for mailbox {mailbox_account_id}"
            )

            # Classify immediately so the UI shows category in real time.
            try:
                from app.services.classification_service import classify_email

                classify_email(str(email.id), self.db)

                logger.info(f"[EMAIL_CLASSIFIED] Email {email.id} categorized immediately")
            except Exception as classify_err:
                logger.error(
                    f"[EMAIL_CLASSIFICATION_FAILED] email={email.id}: {classify_err}"
                )

            # Keep the queue worker as a fallback/background processor.
            try:
                enqueue_task(self.db, task_type="classification", email_id=str(email.id))
                enqueue_task(self.db, task_type="priority", email_id=str(email.id))
            except Exception as enqueue_err:
                logger.error(
                    f"[AI_TASK_ENQUEUE_FAILED] email={email.id}: {enqueue_err}"
                )

            return True, email

        except Exception as e:
            self.db.rollback()

            if isinstance(e, IntegrityError) and (
                "uq_email_provider_msg" in str(e)
                or "duplicate key" in str(e)
                or "uq_email_account_provider_msg_id" in str(e)
            ):
                logger.info(
                    f"[EMAIL_DUPLICATE] Duplicate email "
                    f"{parsed_data.get('provider_message_id')} skipped"
                )
                return False, None

            logger.error(
                f"[EMAIL_ERROR] Failed to save email "
                f"{parsed_data.get('provider_message_id')}: {e}"
            )
            raise e
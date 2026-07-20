import base64
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

def parse_gmail_message(payload_dict: dict) -> dict:
    """
    Parses a raw Gmail JSON payload into a structured dictionary for the database.
    Returns keys matching the Email model.
    """
    parsed = {
        "provider_message_id": payload_dict.get("id"),
        "provider_thread_id": payload_dict.get("threadId"),
        "sender_email": None,
        "to_recipients": [],
        "cc_recipients": [],
        "bcc_recipients": [],
        "subject": None,
        "received_at": None,
        "is_read": True,
        "has_attachments": False,
        "body_text": None,
        "body_html": None,
        "snippet": payload_dict.get("snippet"),
        "labels": payload_dict.get("labelIds", []),
        "raw_email_json": payload_dict
    }

    # Extract labels
    labels = payload_dict.get("labelIds", [])
    if "UNREAD" in labels:
        parsed["is_read"] = False

    payload = payload_dict.get("payload", {})
    headers = payload.get("headers", [])

    for header in headers:
        name = header.get("name", "").lower()
        value = header.get("value", "")
        if name == "from":
            parsed["sender_email"] = value
        elif name == "to":
            parsed["to_recipients"] = [x.strip() for x in value.split(",") if x.strip()]
        elif name == "cc":
            parsed["cc_recipients"] = [x.strip() for x in value.split(",") if x.strip()]
        elif name == "bcc":
            parsed["bcc_recipients"] = [x.strip() for x in value.split(",") if x.strip()]
        elif name == "subject":
            parsed["subject"] = value
        elif name == "date":
            try:
                parsed["received_at"] = parsedate_to_datetime(value)
            except Exception as e:
                logger.warning(f"Failed to parse Date header '{value}': {e}")

    # Fallback to internalDate if Date header parsing failed or is missing
    if not parsed["received_at"] and "internalDate" in payload_dict:
        try:
            timestamp = int(payload_dict["internalDate"]) / 1000.0
            parsed["received_at"] = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except Exception as e:
            logger.warning(f"Failed to parse internalDate: {e}")

    # Extract body parts and attachments
    def walk_parts(parts):
        for part in parts:
            mime_type = part.get("mimeType", "")
            filename = part.get("filename", "")
            
            if filename and part.get("body", {}).get("attachmentId"):
                parsed["has_attachments"] = True

            body_data = part.get("body", {}).get("data")
            if body_data:
                try:
                    decoded = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")
                    if mime_type == "text/plain" and not parsed["body_text"]:
                        parsed["body_text"] = decoded
                    elif mime_type == "text/html" and not parsed["body_html"]:
                        parsed["body_html"] = decoded
                except Exception as e:
                    logger.warning(f"Failed to decode body part: {e}")

            if "parts" in part:
                walk_parts(part["parts"])

    if "parts" in payload:
        walk_parts(payload["parts"])
    else:
        mime_type = payload.get("mimeType", "")
        body_data = payload.get("body", {}).get("data")
        if body_data:
            try:
                decoded = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")
                if mime_type == "text/plain":
                    parsed["body_text"] = decoded
                elif mime_type == "text/html":
                    parsed["body_html"] = decoded
            except Exception as e:
                logger.warning(f"Failed to decode body: {e}")

    return parsed

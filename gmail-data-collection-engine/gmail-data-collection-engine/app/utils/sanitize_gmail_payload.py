import copy
from typing import Any, Dict

def sanitize_gmail_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitizes the raw Gmail JSON payload before storing it in the database.
    - Removes attachment binary/base64 data (body.data) to prevent database bloat.
    - Retains MIME structure, headers, labels, and attachment metadata.
    """
    if not payload:
        return {}

    sanitized = copy.deepcopy(payload)

    def _clean_parts(parts: list):
        for part in parts:
            body = part.get("body", {})
            
            # Identify if this part is an attachment
            filename = part.get("filename", "")
            attachment_id = body.get("attachmentId")
            
            if attachment_id or filename:
                if "data" in body:
                    # Remove the base64 data to save DB space
                    del body["data"]

            # Recursively clean sub-parts (e.g. multipart/mixed containing multipart/alternative)
            if "parts" in part:
                _clean_parts(part["parts"])

    if "payload" in sanitized:
        main_payload = sanitized["payload"]
        
        # Sometimes the main payload itself has a body with attachment data (rare but possible)
        body = main_payload.get("body", {})
        if body.get("attachmentId") and "data" in body:
            del body["data"]
            
        if "parts" in main_payload:
            _clean_parts(main_payload["parts"])
            
    return sanitized

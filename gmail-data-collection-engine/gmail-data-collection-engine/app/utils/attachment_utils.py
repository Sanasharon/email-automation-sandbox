import re
import base64
from typing import List, Dict, Any

UNSAFE_EXTENSIONS = {'.exe', '.bat', '.cmd', '.sh', '.js', '.vbs', '.msi'}

def sanitize_filename(filename: str) -> str:
    if not filename:
        return "unnamed_attachment"
    safe_name = re.sub(r'[^a-zA-Z0-9.\-_]', '_', filename)
    return safe_name

def is_safe_file_type(filename: str) -> bool:
    if not filename:
        return True
    ext = filename.lower()
    for unsafe_ext in UNSAFE_EXTENSIONS:
        if ext.endswith(unsafe_ext):
            return False
    return True

def generate_storage_path(mailbox_account_id: str, provider_message_id: str, provider_attachment_id: str, filename: str) -> str:
    safe_name = sanitize_filename(filename)
    return f"{mailbox_account_id}/{provider_message_id}/{provider_attachment_id}_{safe_name}"

def decode_base64url(data: str) -> bytes:
    if not data:
        return b""
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)

def extract_attachments(raw_email_json: dict) -> List[Dict[str, Any]]:
    attachments = []
    
    def walk_parts(parts):
        for part in parts:
            filename = part.get("filename", "")
            mime_type = part.get("mimeType", "")
            attachment_id = part.get("body", {}).get("attachmentId")
            size = part.get("body", {}).get("size", 0)
            
            disposition = ""
            for header in part.get("headers", []):
                if header.get("name", "").lower() == "content-disposition":
                    disposition = header.get("value", "").lower()
            
            # Skip inline attachments because schema lacks is_inline, and we only want true attachments in Phase 5
            if attachment_id and "inline" not in disposition:
                attachments.append({
                    "provider_attachment_id": attachment_id,
                    "filename": filename,
                    "mime_type": mime_type,
                    "size": size
                })
            
            if "parts" in part:
                walk_parts(part["parts"])

    if "payload" in raw_email_json and "parts" in raw_email_json["payload"]:
        walk_parts(raw_email_json["payload"]["parts"])
        
    return attachments

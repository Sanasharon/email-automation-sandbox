"""
Token & Secret Encryption Utility.
Provides Fernet-based encryption for OAuth tokens and API keys at rest.
"""
import os
import json
import base64
import logging
from cryptography.fernet import Fernet
from app.config import settings

logger = logging.getLogger(__name__)

_fernet = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key = settings.token_encryption_key
        if not key:
            raise RuntimeError("TOKEN_ENCRYPTION_KEY is not set in environment")
        key_bytes = key.encode() if isinstance(key, str) else key
        if len(key_bytes) < 32:
            key_bytes = base64.urlsafe_b64encode(key_bytes.ljust(32, b'=')[:32])
        _fernet = Fernet(key_bytes)
    return _fernet


def encrypt_string(plaintext: str) -> str:
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_string(ciphertext: str) -> str:
    f = _get_fernet()
    return f.decrypt(ciphertext.encode()).decode()


def encrypt_dict(data: dict) -> str:
    return encrypt_string(json.dumps(data))


def decrypt_dict(ciphertext: str) -> dict:
    return json.loads(decrypt_string(ciphertext))


def encrypt_token_file(token_file: str):
    """Encrypts an existing plain-text token.json file in place."""
    if not os.path.exists(token_file):
        return
    with open(token_file, 'r') as f:
        plaintext = f.read()
    encrypted = encrypt_string(plaintext)
    with open(token_file, 'w') as f:
        f.write(encrypted)
    logger.info(f"Encrypted token file: {token_file}")


def decrypt_token_file(token_file: str) -> str:
    """Reads and decrypts a token file, returning the JSON string."""
    if not os.path.exists(token_file):
        return None
    with open(token_file, 'r') as f:
        content = f.read()
    try:
        return decrypt_string(content)
    except Exception:
        return content


def read_token_json(token_file: str) -> dict:
    """Reads token file, decrypting if needed, and returns parsed JSON."""
    if not os.path.exists(token_file):
        return None
    content = decrypt_token_file(token_file)
    if content is None:
        return None
    try:
        return json.loads(content)
    except (json.JSONDecodeError, Exception):
        return None


def write_token_json(token_file: str, data: dict):
    """Writes token data as encrypted JSON to disk."""
    os.makedirs(os.path.dirname(token_file), exist_ok=True)
    encrypted = encrypt_string(json.dumps(data))
    with open(token_file, 'w') as f:
        f.write(encrypted)
    logger.info(f"Wrote encrypted token to: {token_file}")

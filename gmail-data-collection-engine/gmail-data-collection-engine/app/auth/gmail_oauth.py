import os
import json
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.config import settings
from app.auth.encryption import encrypt_string, decrypt_string, read_token_json, write_token_json

logger = logging.getLogger(__name__)

def validate_credential_file(file_path: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Credential file not found at {file_path}")

    with open(file_path, "r") as f:
        try:
            creds_data = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Credential file {file_path} is not valid JSON.")

    if "web" in creds_data and "installed" not in creds_data:
        raise ValueError("Invalid credential type: Expected Desktop OAuth (installed), got Web OAuth.")
    if "installed" not in creds_data:
        raise ValueError(f"Invalid credential format in {file_path}. Expected 'installed' key.")

class NonInteractiveAuthRequired(Exception):
    """Raised when background/non-interactive OAuth flow encounters invalid credentials."""
    pass


def get_gmail_credentials(interactive: bool = True) -> Credentials:
    """
    Manages the Desktop OAuth flow with encrypted token storage.
    Validates scope, handles token reuse and refresh, or initiates a browser flow.
    If interactive=False, raises NonInteractiveAuthRequired instead of opening a GUI browser.
    """
    token_file = settings.google_token_file
    secrets_file = settings.google_client_secrets_file
    required_scope = settings.google_oauth_scopes

    os.makedirs(os.path.dirname(token_file), exist_ok=True)
    validate_credential_file(secrets_file)

    creds = None
    if os.path.exists(token_file):
        try:
            token_data = read_token_json(token_file)
            if token_data:
                creds = Credentials.from_authorized_user_info(token_data)
        except Exception as e:
            logger.warning(f"Failed to load/decrypt existing token file: {e}")
            creds = None

    if creds and creds.valid:
        if required_scope not in creds.scopes:
            logger.info("Existing token missing required scope. Re-authenticating...")
            creds = None
    
    if creds and creds.expired and creds.refresh_token:
        if required_scope in creds.scopes:
            try:
                creds.refresh(Request())
                write_token_json(token_file, json.loads(creds.to_json()))
            except Exception as e:
                logger.warning("Failed to refresh token. Re-authenticating...")
                creds = None
        else:
            creds = None

    if not creds or not creds.valid:
        if not interactive:
            logger.warning("[AUTH] Non-interactive OAuth check: Credentials missing or invalid. Skipping browser flow.")
            raise NonInteractiveAuthRequired("OAuth credentials missing or expired. Interactive login required.")
            
        logger.info("Initiating browser OAuth flow with Account Chooser...")
        flow = InstalledAppFlow.from_client_secrets_file(
            secrets_file, [required_scope]
        )
        creds = flow.run_local_server(port=0, prompt='consent select_account')
        
        write_token_json(token_file, json.loads(creds.to_json()))

    return creds

def create_gmail_service(creds: Credentials):
    """Creates a Gmail API service resource."""
    return build('gmail', 'v1', credentials=creds)

def get_authenticated_gmail_profile(service) -> dict:
    """Fetches the authenticated user's Gmail profile."""
    return service.users().getProfile(userId='me').execute()

def clear_cached_credentials():
    """Deletes cached OAuth token file to force Account Chooser on next login."""
    token_file = settings.google_token_file
    if os.path.exists(token_file):
        try:
            os.remove(token_file)
            logger.info(f"Cleared cached token file at {token_file}")
        except Exception as e:
            logger.error(f"Failed to remove token file: {e}")

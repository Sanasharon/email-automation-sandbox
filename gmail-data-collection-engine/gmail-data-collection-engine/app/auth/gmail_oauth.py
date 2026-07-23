import os
import json
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.config import settings

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

def get_gmail_credentials() -> Credentials:
    """
    Manages the Desktop OAuth flow.
    Validates scope, handles token reuse and refresh, or initiates a browser flow.
    """
    token_file = settings.google_token_file
    secrets_file = settings.google_client_secrets_file
    required_scope = settings.google_oauth_scopes

    # Ensure the parent directory for the token file exists safely
    os.makedirs(os.path.dirname(token_file), exist_ok=True)

    validate_credential_file(secrets_file)

    creds = None
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file)
        except Exception as e:
            logger.warning("Failed to load existing token file.")
            creds = None

    # Verify scope and expiry
    if creds and creds.valid:
        if required_scope not in creds.scopes:
            logger.info("Existing token missing required scope. Re-authenticating...")
            creds = None
    
    if creds and creds.expired and creds.refresh_token:
        if required_scope in creds.scopes:
            try:
                creds.refresh(Request())
                with open(token_file, "w") as f:
                    f.write(creds.to_json())
            except Exception as e:
                logger.warning("Failed to refresh token. Re-authenticating...")
                creds = None
        else:
            creds = None

    if not creds or not creds.valid:
        logger.info("Initiating browser OAuth flow with Account Chooser...")
        flow = InstalledAppFlow.from_client_secrets_file(
            secrets_file, [required_scope]
        )
        creds = flow.run_local_server(port=0, prompt='consent select_account')
        
        with open(token_file, "w") as f:
            f.write(creds.to_json())

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

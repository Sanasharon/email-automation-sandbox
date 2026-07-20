from fastapi import APIRouter
from app.auth.gmail_oauth import get_gmail_credentials
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth/gmail", tags=["auth"])

class ConnectResponse(BaseModel):
    status: str
    message: str

@router.post("/connect", response_model=ConnectResponse)
def connect_gmail():
    try:
        creds = get_gmail_credentials()
        if creds and creds.valid:
            return ConnectResponse(status="success", message="Gmail connected successfully.")
        return ConnectResponse(status="error", message="Failed to authenticate.")
    except Exception as e:
        logger.error(f"Error connecting to Gmail: {str(e)}")
        return ConnectResponse(status="error", message="An error occurred during authentication.")

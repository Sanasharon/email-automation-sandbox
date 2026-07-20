from typing import Any, Dict, Optional
from fastapi import Request
from fastapi.responses import JSONResponse
import logging
from app.core.responses import error_response

logger = logging.getLogger(__name__)

class AppException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches all unhandled exceptions globally and formats them into the standard APIErrorResponse.
    """
    request_id = getattr(request.state, "request_id", None)
    
    if isinstance(exc, AppException):
        logger.warning(f"AppException [ID: {request_id}]: {exc.code} - {exc.message}")
        content = error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=request_id
        ).model_dump()
        return JSONResponse(status_code=exc.status_code, content=content)

    # For unknown exceptions
    logger.error(f"Unhandled Exception [ID: {request_id}]: {str(exc)}", exc_info=True)
    content = error_response(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred. Please try again later.",
        request_id=request_id
    ).model_dump()
    return JSONResponse(status_code=500, content=content)

from sqlalchemy.orm import Session
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

class BaseService:
    def __init__(self, db: Session):
        self.db = db

    def execute_in_transaction(self, operation: Callable[..., Any], *args, **kwargs) -> Any:
        """Executes a function within a database transaction."""
        try:
            result = operation(*args, **kwargs)
            self.db.commit()
            return result
        except Exception as e:
            self.db.rollback()
            logger.error(f"Transaction failed: {str(e)}")
            raise

    def validate_or_fail(self, condition: bool, error_message: str):
        """Helper for business rule validation"""
        if not condition:
            from app.core.exceptions import AppException
            raise AppException(message=error_message, code="VALIDATION_FAILED", status_code=400)

    def log_audit(self, action: str, entity_id: str, details: str = ""):
        """Stub for audit logging, can be hooked into a DB table later."""
        logger.info(f"AUDIT | Action: {action} | Entity: {entity_id} | Details: {details}")

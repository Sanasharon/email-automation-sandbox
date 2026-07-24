"""
System Logger — Writes structured events to the system_logs table.
Covers: sync, scheduler, oauth, workflow, AI, and system events.
"""
import logging
import traceback
from datetime import datetime, timezone
from app.db.session import SessionLocal
from app.models.system_log import SystemLog

logger = logging.getLogger("system_logger")


def _write_log(level: str, category: str, message: str, details: dict = None, user_id: str = None):
    try:
        db = SessionLocal()
        try:
            log_entry = SystemLog(
                level=level,
                category=category,
                message=message,
                details=details,
                user_id=user_id,
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to write system log: {e}")
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Failed to create DB session for system log: {e}")


def log_sync_event(level: str, message: str, mailbox_id: str = None, details: dict = None, user_id: str = None):
    _write_log(level, "sync", message, details or {"mailbox_id": mailbox_id}, user_id)


def log_scheduler_event(level: str, message: str, details: dict = None):
    _write_log(level, "scheduler", message, details)


def log_oauth_event(level: str, message: str, details: dict = None, user_id: str = None):
    _write_log(level, "oauth", message, details, user_id)


def log_workflow_event(level: str, message: str, workflow_id: str = None, email_id: str = None, details: dict = None, user_id: str = None):
    extra = details or {}
    if workflow_id:
        extra["workflow_id"] = workflow_id
    if email_id:
        extra["email_id"] = email_id
    _write_log(level, "workflow", message, extra, user_id)


def log_ai_event(level: str, message: str, provider: str = None, details: dict = None, user_id: str = None):
    extra = details or {}
    if provider:
        extra["provider"] = provider
    _write_log(level, "ai", message, extra, user_id)


def log_system_event(level: str, message: str, details: dict = None, user_id: str = None):
    _write_log(level, "system", message, details, user_id)


def log_auth_event(level: str, message: str, details: dict = None, user_id: str = None):
    _write_log(level, "auth", message, details, user_id)

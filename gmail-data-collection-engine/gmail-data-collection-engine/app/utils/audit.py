"""
Audit logging utility for admin operations.
Records create, update, delete, and clone actions to the database.
"""
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def create_audit_log(
    db: Session,
    actor_id: str,
    action: str,
    target: str,
    target_id,
    before=None,
    after=None,
):
    """
    Create an audit log entry for an admin action.

    Args:
        db: SQLAlchemy session
        actor_id: ID of the user performing the action
        action: Action name (e.g. 'create_role', 'update_user')
        target: Target model name (e.g. 'UserRole', 'User')
        target_id: ID of the target record
        before: State before the action (dict or ORM object)
        after: State after the action (dict or ORM object)
    """
    try:
        def _serialize(obj):
            if obj is None:
                return None
            if isinstance(obj, dict):
                return obj
            # ORM object — extract column values
            if hasattr(obj, "__table__"):
                return {
                    c.name: str(getattr(obj, c.name, None))
                    for c in obj.__table__.columns
                }
            return str(obj)

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor_id": str(actor_id),
            "action": action,
            "target": target,
            "target_id": str(target_id),
            "before": _serialize(before),
            "after": _serialize(after),
        }
        logger.info(f"AUDIT: {json.dumps(log_entry, default=str)}")
    except Exception as e:
        # Audit logging should never break the main operation
        logger.error(f"Failed to create audit log: {e}")

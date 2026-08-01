# app/services/ai_task_service.py
"""
AI Task queue service: enqueue tasks, fetch pending tasks, and process them.
This file is designed to be used by the scheduler worker (process_ai_tasks_job).
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.ai_task import AiTask
from app.models.email import Email
from app.services.classification_service import classify_email as classify_email_sync
from app.services.priority_service import classify_email_priority as classify_priority_sync

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 10


def enqueue_task(
    db: Session,
    task_type: str,
    email_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    scheduled_at: Optional[datetime] = None,
    max_attempts: int = 3,
) -> AiTask:
    """
    Insert a new ai_tasks row and return it.
    """
    task = AiTask(
        task_type=task_type,
        email_id=email_id,
        payload=payload or {},
        scheduled_at=scheduled_at,
        max_attempts=max_attempts,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info(f"[AI_TASK] Enqueued task {task.id} type={task.task_type} email_id={task.email_id}")
    return task


def fetch_pending_tasks(db: Session, limit: int = DEFAULT_BATCH_SIZE) -> List[AiTask]:
    """
    Fetch pending tasks whose scheduled_at is NULL or <= now, ordered by creation time.
    """
    now = datetime.now(timezone.utc)
    q = (
        db.query(AiTask)
        .filter(
            AiTask.status == "pending",
        )
        .filter((AiTask.scheduled_at == None) | (AiTask.scheduled_at <= now))
        .order_by(AiTask.created_at)
        .limit(limit)
    )
    return q.all()


def mark_task_processing(db: Session, task: AiTask) -> AiTask:
    task.status = "processing"
    task.started_at = datetime.now(timezone.utc)
    task.attempts = (task.attempts or 0) + 1
    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info(f"[AI_TASK] Marked processing {task.id} (attempts={task.attempts})")
    return task


def mark_task_completed(db: Session, task: AiTask, result: Dict[str, Any]) -> AiTask:
    task.status = "completed"
    task.result = result
    task.completed_at = datetime.now(timezone.utc)
    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info(f"[AI_TASK] Task completed {task.id}")
    return task


def mark_task_failed(db: Session, task: AiTask, error: str) -> AiTask:
    task.error = (error[:4000] if error else error)  # truncate long errors
    task.updated_at = datetime.now(timezone.utc)
    # if attempts < max_attempts -> requeue (pending) else mark failed
    if (task.attempts or 0) < (task.max_attempts or 3):
        task.status = "pending"
    else:
        task.status = "failed"
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.warning(f"[AI_TASK] Task {task.id} marked {task.status}. Error: {task.error}")
    return task


def process_task(db: Session, task: AiTask) -> Dict[str, Any]:
    """
    Execute a single task synchronously (called by worker).
    Supported task_type values:
      - 'classification' : calls classification_service.classify_email(email_id)
      - 'priority'       : calls priority_service.classify_email_priority(email_id)
    Returns a result dict describing success or failure.
    """
    logger.info(f"[AI_TASK] Processing task {task.id} type={task.task_type} email_id={task.email_id}")
    try:
        if task.task_type == "classification":
            if not task.email_id:
                return {"success": False, "error": "classification task requires email_id"}
            # classification_service persists email_categories
            data = classify_email_sync(str(task.email_id), db=db)
            return {"success": True, "data": data}
        elif task.task_type == "priority":
            if not task.email_id:
                return {"success": False, "error": "priority task requires email_id"}
            data = classify_priority_sync(str(task.email_id), db=db, persist=True)
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": f"Unsupported task type: {task.task_type}"}
    except Exception as exc:
        logger.exception("Error processing AI task %s", task.id)
        return {"success": False, "error": str(exc)}


def process_pending_tasks(db: Optional[Session] = None, batch_size: int = DEFAULT_BATCH_SIZE) -> int:
    """
    Fetch pending tasks and process them in a loop.
    Returns number of processed tasks.
    If db is None, a local SessionLocal is used and closed at the end.
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    processed = 0
    try:
        tasks = fetch_pending_tasks(db, limit=batch_size)
        logger.info(f"[AI_TASK] Fetched {len(tasks)} pending task(s)")
        for task in tasks:
            # if task already exceeded attempts and is failed, skip
            if (task.attempts or 0) >= (task.max_attempts or 3) and task.status == "failed":
                logger.info(f"[AI_TASK] Skipping failed task {task.id} (attempts >= max_attempts)")
                continue
            try:
                mark_task_processing(db, task)
                result = process_task(db, task)
                if result.get("success"):
                    mark_task_completed(db, task, result.get("data"))
                else:
                    mark_task_failed(db, task, result.get("error", "unknown"))
                processed += 1
            except Exception as exc:
                # ensure we mark failure and continue with next tasks
                logger.exception("Unhandled exception while processing task %s", task.id)
                mark_task_failed(db, task, str(exc))
    finally:
        if close_db:
            db.close()
    return processed
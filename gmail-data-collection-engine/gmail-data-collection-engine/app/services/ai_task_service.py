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
from app.models.category import Category
from app.models.email_category import EmailCategory
from app.services.classification_service import classify_email as classify_email_sync, classify_text
from app.services.priority_service import classify_email_priority as classify_priority_sync, classify_text_priority

# Task types that must both complete before an email is considered fully AI-processed.
# Extend this if new per-email AI task types are added.
EMAIL_TASK_TYPES = {"classification", "priority"}

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

    # Reflect the queued state on the email itself so analytics/monitoring
    # can immediately show it as "pending" rather than "not_started".
    if email_id and task_type in EMAIL_TASK_TYPES:
        email = db.query(Email).filter(Email.id == email_id).one_or_none()
        if email and email.ai_processing_status == "not_started":
            email.ai_processing_status = "pending"
            db.add(email)
            db.commit()

    return task


def _sync_email_ai_status(db: Session, email_id: str) -> None:
    """
    Recompute Email.ai_processing_status from the current state of its
    classification/priority tasks:
      - completed  -> all EMAIL_TASK_TYPES tasks completed
      - failed     -> at least one EMAIL_TASK_TYPES task permanently failed
                      and none are still pending/processing
      - pending    -> otherwise, if any task exists
    Leaves ai_processed_at set the first time the email reaches "completed".
    """
    if not email_id:
        return
    email = db.query(Email).filter(Email.id == email_id).one_or_none()
    if not email:
        return

    tasks = (
        db.query(AiTask)
        .filter(AiTask.email_id == email_id, AiTask.task_type.in_(EMAIL_TASK_TYPES))
        .all()
    )
    if not tasks:
        return

    statuses = {t.status for t in tasks}
    if statuses <= {"completed"}:
        new_status = "completed"
    elif "pending" in statuses or "processing" in statuses:
        new_status = "pending"
    elif "failed" in statuses:
        new_status = "failed"
    else:
        new_status = email.ai_processing_status

    if new_status != email.ai_processing_status:
        email.ai_processing_status = new_status
        if new_status == "completed" and not email.ai_processed_at:
            email.ai_processed_at = datetime.now(timezone.utc)
        db.add(email)
        db.commit()


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
    if task.email_id:
        _sync_email_ai_status(db, str(task.email_id))
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
    if task.status == "failed" and task.email_id:
        _sync_email_ai_status(db, str(task.email_id))
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


def _process_email_task_pair(db: Session, classification_task: AiTask, priority_task: AiTask) -> None:
    """
    Compute classification + priority for the same email and persist both
    Email.category and Email.priority in a single commit, so the two
    badges become visible to clients at the same moment instead of
    category landing first and priority following once its own task
    finishes.

    Uses the non-persisting classify_text()/classify_text_priority() helpers
    (rather than classify_email_sync/classify_priority_sync, which each
    commit independently) and replicates their existing persistence logic
    here so the two writes can share one transaction.

    Each AiTask is still marked processing/completed/failed individually,
    so per-task retries, attempts, and error messages are unaffected. If
    either computation fails, that task alone is marked failed (eligible
    for its normal retry) while the other's result is still committed.
    """
    email_id = str(classification_task.email_id)
    classification_result: Optional[List[Dict[str, Any]]] = None
    classification_error: Optional[str] = None
    priority_result: Optional[Dict[str, Any]] = None
    priority_error: Optional[str] = None

    email = db.query(Email).filter(Email.id == email_id).one_or_none()
    if not email:
        classification_error = priority_error = "Email not found"
    else:
        content = "\n\n".join(
            part for part in [email.subject, email.body_text, email.snippet] if part
        )

        try:
            predictions = classify_text(content, db=db, top_k=3)
            persisted = []
            for p in predictions:
                category_name = (p.get("category") or "").strip()
                if not category_name:
                    continue
                confidence = float(p.get("confidence", 0.0))
                cat = db.query(Category).filter(Category.name.ilike(category_name)).one_or_none()
                if not cat:
                    cat = Category(name=category_name.title(), description=None)
                    db.add(cat)
                    db.flush()
                assoc = (
                    db.query(EmailCategory)
                    .filter(EmailCategory.email_id == email.id, EmailCategory.category_id == cat.id)
                    .one_or_none()
                )
                if not assoc:
                    assoc = EmailCategory(email_id=email.id, category_id=cat.id, confidence=confidence)
                    db.add(assoc)
                else:
                    assoc.confidence = confidence
                persisted.append({"category": cat.name, "category_id": str(cat.id), "confidence": confidence})
            if persisted:
                top = max(persisted, key=lambda p: p["confidence"])
                email.category = top["category"]
            classification_result = persisted
        except Exception as exc:
            logger.exception("Error computing classification for paired task %s", classification_task.id)
            classification_error = str(exc)

        try:
            pr = classify_text_priority(content, db=db, sender_email=email.sender_email)
            email.priority = pr.get("priority", "Medium")
            email.priority_confidence = float(pr.get("confidence", 0.0))
            priority_result = {"priority": email.priority, "confidence": email.priority_confidence}
        except Exception as exc:
            logger.exception("Error computing priority for paired task %s", priority_task.id)
            priority_error = str(exc)

        db.add(email)
        db.commit()
        db.refresh(email)

    if classification_error is None:
        mark_task_completed(db, classification_task, classification_result)
    else:
        mark_task_failed(db, classification_task, classification_error)

    if priority_error is None:
        mark_task_completed(db, priority_task, priority_result)
    else:
        mark_task_failed(db, priority_task, priority_error)


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

        # Group classification/priority tasks by email so a same-batch pair
        # can be routed through _process_email_task_pair() and committed
        # together. Tasks without a matching counterpart in this batch fall
        # through to the existing independent per-task handling below.
        pending_by_email: Dict[str, Dict[str, AiTask]] = {}
        for task in tasks:
            if task.task_type in EMAIL_TASK_TYPES and task.email_id:
                pending_by_email.setdefault(str(task.email_id), {})[task.task_type] = task
        paired_task_ids = set()
        for task_map in pending_by_email.values():
            if "classification" in task_map and "priority" in task_map:
                paired_task_ids.add(task_map["classification"].id)
                paired_task_ids.add(task_map["priority"].id)

        handled_email_pairs = set()
        for task in tasks:
            # if task already exceeded attempts and is failed, skip
            if (task.attempts or 0) >= (task.max_attempts or 3) and task.status == "failed":
                logger.info(f"[AI_TASK] Skipping failed task {task.id} (attempts >= max_attempts)")
                continue
            try:
                if task.id in paired_task_ids:
                    email_id = str(task.email_id)
                    if email_id in handled_email_pairs:
                        continue  # already processed together with its pair
                    task_map = pending_by_email[email_id]
                    mark_task_processing(db, task_map["classification"])
                    mark_task_processing(db, task_map["priority"])
                    _process_email_task_pair(db, task_map["classification"], task_map["priority"])
                    handled_email_pairs.add(email_id)
                    processed += 2
                else:
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
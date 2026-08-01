# app/api/v1/ai_tasks.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ai_task import AiTaskCreate, AiTaskResponse
from app.services.ai_task_service import enqueue_task
from app.models.ai_task import AiTask

from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/ai-tasks", tags=["ai-tasks"])

def _require_admin(user = Depends(get_current_user)):
    """
    Simple admin guard — adapt if your project has a different permission model.
    """
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user

@router.post("/", response_model=AiTaskResponse, status_code=status.HTTP_202_ACCEPTED)
def create_task(payload: AiTaskCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Enqueue a new AI task.

    Example payload:
    {
      "email_id": "uuid-or-null",
      "task_type": "classification",   # or "priority"
      "payload": { ... },              # optional
      "scheduled_at": "2026-08-01T12:00:00Z",
      "max_attempts": 3
    }

    Returns the created ai_tasks row (202 Accepted).
    """
    email_id = str(payload.email_id) if payload.email_id else None
    task = enqueue_task(
        db,
        task_type=payload.task_type,
        email_id=email_id,
        payload=payload.payload,
        scheduled_at=payload.scheduled_at,
        max_attempts=payload.max_attempts or 3
    )
    return task

@router.get("/{task_id}", response_model=AiTaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Get a single task by ID.
    """
    t = db.query(AiTask).filter(AiTask.id == task_id).one_or_none()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return t

@router.get("/pending", response_model=List[AiTaskResponse])
def list_pending(db: Session = Depends(get_db), current_user = Depends(_require_admin)):
    """
    List pending tasks (admin only). Returns up to 100 pending tasks ordered by creation time.
    """
    tasks = db.query(AiTask).filter(AiTask.status == 'pending').order_by(AiTask.created_at).limit(100).all()
    return tasks
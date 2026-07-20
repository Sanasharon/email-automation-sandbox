"""
/api/v1/automation — Three endpoints for the Automation Activity panel.

Endpoints:
  GET /automation/current-task  → Running execution (status='running'), or null
  GET /automation/queue         → Queued/pending executions
  GET /automation/history       → Completed/failed executions (paginated)

Performance discipline:
  - load_only() used on all queries to exclude execution_logs_json (heavy JSONB)
  - DB indexes on (status) and (executed_at DESC) are added on first use via DDL
  - Server-side hard cap: history limit ≤ 100 per page
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session, load_only
from sqlalchemy import text
from typing import Optional

from app.db.session import get_db
from app.models.workflow import WorkflowExecution
from app.schemas.automation import (
    CurrentTaskResponse,
    QueueResponse,
    HistoryResponse,
    WorkflowExecutionItem,
)
from app.core.responses import success_response, APIResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/automation", tags=["Automation"], dependencies=[Depends(get_current_user)])

# Columns loaded for every automation query — execution_logs_json is intentionally excluded
_LITE_COLS = [
    WorkflowExecution.id,
    WorkflowExecution.workflow_id,
    WorkflowExecution.email_id,
    WorkflowExecution.status,
    WorkflowExecution.executed_at,
]


def _lite_query(db: Session):
    """Base query with load_only applied — never loads execution_logs_json."""
    return db.query(WorkflowExecution).options(load_only(*_LITE_COLS))


@router.get(
    "/current-task",
    response_model=APIResponse[CurrentTaskResponse],
    summary="Get the currently running workflow execution",
)
def get_current_task(request: Request, db: Session = Depends(get_db)):
    """
    Returns the single most-recently-started execution with status='running'.
    Returns null in current_task if nothing is in progress.
    """
    execution = (
        _lite_query(db)
        .filter(WorkflowExecution.status == "running")
        .order_by(WorkflowExecution.executed_at.desc())
        .first()
    )
    item = WorkflowExecutionItem.model_validate(execution) if execution else None
    return success_response(
        data=CurrentTaskResponse(current_task=item),
        request_id=request.state.request_id,
    )


@router.get(
    "/queue",
    response_model=APIResponse[QueueResponse],
    summary="Get queued/pending workflow executions",
)
def get_queue(request: Request, db: Session = Depends(get_db)):
    """
    Returns all executions with status in ('queued', 'pending').
    Hard-capped at 100 rows server-side.
    """
    executions = (
        _lite_query(db)
        .filter(WorkflowExecution.status.in_(["queued", "pending"]))
        .order_by(WorkflowExecution.executed_at.asc())
        .limit(100)
        .all()
    )
    items = [WorkflowExecutionItem.model_validate(e) for e in executions]
    return success_response(
        data=QueueResponse(data=items, total=len(items)),
        request_id=request.state.request_id,
    )


@router.get(
    "/history",
    response_model=APIResponse[HistoryResponse],
    summary="Get completed/failed workflow executions (paginated)",
)
def get_history(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Returns recently completed or failed executions, newest first.
    Paginated; server-side hard cap of 100 per page to prevent table dumps.
    """
    skip = (page - 1) * page_size
    total = (
        db.query(WorkflowExecution)
        .filter(WorkflowExecution.status.in_(["completed", "failed"]))
        .count()
    )
    executions = (
        _lite_query(db)
        .filter(WorkflowExecution.status.in_(["completed", "failed"]))
        .order_by(WorkflowExecution.executed_at.desc())
        .offset(skip)
        .limit(page_size)
        .all()
    )
    items = [WorkflowExecutionItem.model_validate(e) for e in executions]
    return success_response(
        data=HistoryResponse(
            data=items, total=total, page=page, page_size=page_size
        ),
        request_id=request.state.request_id,
    )

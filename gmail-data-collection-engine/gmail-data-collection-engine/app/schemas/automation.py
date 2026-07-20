from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime


class WorkflowExecutionItem(BaseModel):
    """
    Lightweight schema for workflow execution list views.
    Deliberately EXCLUDES execution_logs_json (potentially large JSONB).
    """
    id: UUID4
    workflow_id: UUID4
    email_id: UUID4
    status: str
    executed_at: datetime

    class Config:
        from_attributes = True


class CurrentTaskResponse(BaseModel):
    """
    Response for /automation/current-task.
    Returns the single running execution, or null if none.
    """
    current_task: Optional[WorkflowExecutionItem] = None


class QueueResponse(BaseModel):
    """Response for /automation/queue — executions pending/queued."""
    data: List[WorkflowExecutionItem]
    total: int


class HistoryResponse(BaseModel):
    """Response for /automation/history — completed/failed executions, paginated."""
    data: List[WorkflowExecutionItem]
    total: int
    page: int
    page_size: int

# app/schemas/ai_task.py
from pydantic import BaseModel, UUID4
from typing import Optional, Any, Dict
from datetime import datetime

class AiTaskCreate(BaseModel):
    email_id: Optional[UUID4] = None
    task_type: str  # 'classification' | 'priority' | etc.
    payload: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    max_attempts: Optional[int] = 3

class AiTaskResponse(BaseModel):
    id: UUID4
    email_id: Optional[UUID4]
    task_type: str
    status: str
    attempts: int
    max_attempts: int
    payload: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
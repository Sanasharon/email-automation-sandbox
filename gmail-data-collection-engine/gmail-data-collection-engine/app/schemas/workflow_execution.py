from pydantic import BaseModel, UUID4
from typing import Dict, Any, Optional

class WorkflowExecutionCreate(BaseModel):
    workflow_id: UUID4
    email_id: UUID4
    status: str
    execution_logs_json: Dict[str, Any]

class WorkflowExecutionUpdate(BaseModel):
    status: Optional[str] = None
    execution_logs_json: Optional[Dict[str, Any]] = None

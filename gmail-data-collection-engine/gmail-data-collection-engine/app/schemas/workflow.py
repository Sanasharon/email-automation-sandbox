from pydantic import BaseModel, ConfigDict, Field, UUID4, constr
from typing import Optional, Dict, Any, List
from datetime import datetime

# ---------------------------------------------------------
# Base Schema (Shared attributes)
# ---------------------------------------------------------
class WorkflowBase(BaseModel):
    name: constr(min_length=3, max_length=150) = Field(..., description="Name of the workflow")
    description: Optional[str] = Field(None, description="Optional description of what the workflow does")
    trigger_conditions_json: Dict[str, Any] = Field(..., description="JSON structure defining triggers")
    actions_json: Dict[str, Any] = Field(..., description="JSON structure defining actions")
    is_active: bool = Field(True, description="Whether the workflow is active and listening for events")

# ---------------------------------------------------------
# Create Schema
# ---------------------------------------------------------
class WorkflowCreate(WorkflowBase):
    mailbox_account_id: UUID4 = Field(..., description="The ID of the mailbox this workflow applies to")

# ---------------------------------------------------------
# Update Schema
# ---------------------------------------------------------
class WorkflowUpdate(BaseModel):
    name: Optional[constr(min_length=3, max_length=150)] = None
    description: Optional[str] = None
    trigger_conditions_json: Optional[Dict[str, Any]] = None
    actions_json: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

# ---------------------------------------------------------
# State Update Schema (For fast toggle)
# ---------------------------------------------------------
class WorkflowStateUpdate(BaseModel):
    action: str = Field(..., description="Must be 'enable' or 'disable'")

# ---------------------------------------------------------
# Response Schema
# ---------------------------------------------------------
class WorkflowResponse(WorkflowBase):
    id: UUID4
    mailbox_account_id: UUID4
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Note: WorkflowListResponse is implicitly handled by PaginatedResponse[WorkflowResponse] from app.common.pagination

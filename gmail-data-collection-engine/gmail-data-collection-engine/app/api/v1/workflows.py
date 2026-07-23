from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from pydantic import UUID4
from app.db.session import get_db
from app.core.responses import success_response, APIResponse
from app.services.workflow_service import WorkflowService
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowStateUpdate, WorkflowResponse
from app.common.pagination import PaginatedResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/workflows", tags=["Workflows"], dependencies=[Depends(get_current_user)])

def get_workflow_service(db: Session = Depends(get_db)) -> WorkflowService:
    return WorkflowService(db)

@router.get("", response_model=APIResponse[PaginatedResponse[WorkflowResponse]])
def get_workflows(
    request: Request,
    status: str = Query("all", description="Filter by status (all, active, disabled)"),
    search: str = Query("", description="Search by workflow name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service)
):
    """List workflows with pagination, status filtering, search, and user scoping."""
    status_filter = status if status in ["active", "disabled"] else None
    search_filter = search if search else None
    
    result = service.get_workflows(status=status_filter, search=search_filter, page=page, page_size=page_size, user_id=current_user["id"])
    return success_response(data=result, request_id=request.state.request_id)

@router.get("/categories", response_model=APIResponse[list[dict]])
def get_categories(request: Request):
    """Returns static dropdown options for workflow trigger categories."""
    categories = [
        {"category": "Billing Complaint", "type": "Customer", "department": "Finance", "priority": "High"},
        {"category": "Technical Support Request", "type": "Customer", "department": "Engineering", "priority": "High"},
        {"category": "Refund Request", "type": "Customer", "department": "Finance", "priority": "Medium"},
        {"category": "General Inquiry", "type": "Customer", "department": "Support", "priority": "Low"},
        {"category": "Internal Escalation", "type": "Internal", "department": "Varies", "priority": "High"}
    ]
    return success_response(data=categories, request_id=request.state.request_id)

@router.get("/{id}", response_model=APIResponse[WorkflowResponse])
def get_workflow(
    id: UUID4,
    request: Request,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Get a single workflow by ID."""
    workflow = service.get_workflow(str(id))
    return success_response(data=workflow, request_id=request.state.request_id)

@router.post("", response_model=APIResponse[WorkflowResponse])
def create_workflow(
    workflow_in: WorkflowCreate,
    request: Request,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Create a new workflow."""
    workflow = service.create_workflow(workflow_in)
    return success_response(data=workflow, message="Workflow created successfully", request_id=request.state.request_id)

@router.put("/{id}", response_model=APIResponse[WorkflowResponse])
def update_workflow(
    id: UUID4,
    workflow_in: WorkflowUpdate,
    request: Request,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Update an existing workflow."""
    workflow = service.update_workflow(str(id), workflow_in)
    return success_response(data=workflow, message="Workflow updated successfully", request_id=request.state.request_id)

@router.patch("/{id}/state", response_model=APIResponse[WorkflowResponse])
def toggle_workflow_state(
    id: UUID4,
    state_in: WorkflowStateUpdate,
    request: Request,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Fast toggle for enabling/disabling a workflow."""
    workflow = service.toggle_state(str(id), state_in.action)
    return success_response(data=workflow, message=f"Workflow {state_in.action}d successfully", request_id=request.state.request_id)

@router.delete("/{id}", response_model=APIResponse[bool])
def delete_workflow(
    id: UUID4,
    request: Request,
    service: WorkflowService = Depends(get_workflow_service)
):
    """Hard delete a workflow."""
    success = service.delete_workflow(str(id))
    return success_response(data=success, message="Workflow deleted successfully", request_id=request.state.request_id)

from app.models.workflow import WorkflowExecution
@router.get("/{id}/executions", response_model=APIResponse[list[dict]])
def get_workflow_executions(
    id: UUID4,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get the last 10 executions for a specific workflow."""
    executions = (
        db.query(WorkflowExecution)
        .filter(WorkflowExecution.workflow_id == id)
        .order_by(WorkflowExecution.executed_at.desc())
        .limit(10)
        .all()
    )
    # Serialize manually for simplicity
    results = [
        {
            "id": str(ex.id),
            "email_id": str(ex.email_id),
            "status": ex.status,
            "executed_at": ex.executed_at.isoformat() if ex.executed_at else None,
            "logs": ex.execution_logs_json
        }
        for ex in executions
    ]
    return success_response(data=results, request_id=request.state.request_id)

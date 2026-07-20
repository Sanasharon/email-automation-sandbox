from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardSummaryResponse, RecentActivityResponse
from app.core.responses import success_response, APIResponse
from fastapi import Request
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard Foundation"], dependencies=[Depends(get_current_user)])

def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db)

@router.get("/summary", response_model=APIResponse[DashboardSummaryResponse], summary="Get Dashboard Summary KPIs")
def get_summary(request: Request, service: DashboardService = Depends(get_dashboard_service)):
    """Returns aggregated metrics from the Gmail Collection Layer and Workflow executions."""
    return success_response(data=service.get_summary(), request_id=request.state.request_id)

@router.get("/recent-activity", response_model=APIResponse[RecentActivityResponse], summary="Get Recent Activity Feed")
def get_recent_activity(request: Request, service: DashboardService = Depends(get_dashboard_service)):
    """Returns a unified timeline of recent system events, errors, and workflow executions."""
    return success_response(data=service.get_recent_activity(), request_id=request.state.request_id)

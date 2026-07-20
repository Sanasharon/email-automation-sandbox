from pydantic import BaseModel
from typing import List, Optional

class EmailVolumeSeries(BaseModel):
    time: str
    incoming: int
    automated: int

class DashboardSummaryResponse(BaseModel):
    total_workflows: int
    active_workflows: int
    emails_processed: int
    successful_executions: int
    failed_executions: int
    pending_jobs: int
    system_health_percent: float
    email_volume_series: List[EmailVolumeSeries]

class RecentActivityItem(BaseModel):
    id: str
    type: str
    title: str
    description: str
    timestamp: str
    status: str

class RecentActivityResponse(BaseModel):
    data: List[RecentActivityItem]

# app/schemas/analytics.py
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class CategoryCount(BaseModel):
    category_name: str
    count: int

class PriorityCount(BaseModel):
    priority: str
    count: int

class Totals(BaseModel):
    total_emails: int
    processed_count: int
    processing_backlog: int

class TaskSummary(BaseModel):
    pending_tasks: int
    failed_tasks_last_24h: int

class SummaryResponse(BaseModel):
    category_counts: List[CategoryCount]
    priority_counts: List[PriorityCount]
    totals: Totals
    task_summary: TaskSummary

class DailyPoint(BaseModel):
    day: str
    count: int

class DailyTrendsResponse(BaseModel):
    days: int
    data: List[DailyPoint]

class ProcessingTimesResponse(BaseModel):
    avg_seconds: Optional[float]
    median_seconds: Optional[float]
    p90_seconds: Optional[float]
    processed_count: int

class MonitoringHealthResponse(BaseModel):
    db_ok: bool
    pending_tasks: int
    recent_errors: List[Dict[str, Any]]
from sqlalchemy.orm import Session
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import DashboardSummaryResponse, EmailVolumeSeries, RecentActivityResponse, RecentActivityItem

class DashboardService:
    def __init__(self, db: Session):
        self.repository = DashboardRepository(db)

    def get_summary(self) -> DashboardSummaryResponse:
        total_workflows = self.repository.get_total_workflows()
        active_workflows = self.repository.get_active_workflows()
        emails_processed = self.repository.get_emails_processed()
        successful_executions = self.repository.get_successful_executions()
        failed_executions = self.repository.get_failed_executions()
        pending_jobs = self.repository.get_pending_executions()

        # Calculate system health based on execution success rate and sync errors
        total_executions = successful_executions + failed_executions
        health_percent = 100.0
        if total_executions > 0:
            health_percent = (successful_executions / total_executions) * 100.0

        # Fetch real time series data from the database
        raw_series = self.repository.get_email_volume_series()
        volume_series = [
            EmailVolumeSeries(time=row["time"], incoming=row["incoming"], automated=row["automated"])
            for row in raw_series
        ]

        return DashboardSummaryResponse(
            total_workflows=total_workflows,
            active_workflows=active_workflows,
            emails_processed=emails_processed,
            successful_executions=successful_executions,
            failed_executions=failed_executions,
            pending_jobs=pending_jobs,
            system_health_percent=round(health_percent, 1),
            email_volume_series=volume_series
        )

    def get_recent_activity(self) -> RecentActivityResponse:
        recent_errors = self.repository.get_recent_sync_errors(limit=2)
        recent_executions = self.repository.get_recent_workflow_executions(limit=2)

        activities = []
        for error in recent_errors:
            activities.append(RecentActivityItem(
                id=f"err_{error.id}",
                type="email_error",
                title=f"Sync Error: {error.error_type}",
                description=error.error_message or "Unknown error",
                timestamp=error.created_at.isoformat(),
                status="error"
            ))

        for exec_row in recent_executions:
            status_map = {"success": "success", "failed": "error", "pending": "info"}
            activities.append(RecentActivityItem(
                id=f"exec_{exec_row.id}",
                type="workflow_execution",
                title=f"Workflow {exec_row.status.capitalize()}",
                description=f"Execution for workflow ID {exec_row.workflow_id}",
                timestamp=exec_row.executed_at.isoformat(),
                status=status_map.get(exec_row.status, "info")
            ))

        # Sort combined activities by timestamp descending
        activities.sort(key=lambda x: x.timestamp, reverse=True)

        return RecentActivityResponse(data=activities)

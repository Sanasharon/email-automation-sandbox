from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models import Email, Workflow, WorkflowExecution, SyncLog, SyncError

class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_total_workflows(self) -> int:
        return self.db.query(func.count(Workflow.id)).scalar() or 0

    def get_active_workflows(self) -> int:
        return self.db.query(func.count(Workflow.id)).filter(Workflow.is_active == True).scalar() or 0

    def get_emails_processed(self) -> int:
        return self.db.query(func.count(Email.id)).scalar() or 0

    def get_successful_executions(self) -> int:
        return self.db.query(func.count(WorkflowExecution.id)).filter(WorkflowExecution.status == 'success').scalar() or 0

    def get_failed_executions(self) -> int:
        return self.db.query(func.count(WorkflowExecution.id)).filter(WorkflowExecution.status == 'failed').scalar() or 0

    def get_pending_executions(self) -> int:
        return self.db.query(func.count(WorkflowExecution.id)).filter(WorkflowExecution.status == 'pending').scalar() or 0

    def get_recent_sync_errors(self, limit: int = 5):
        return self.db.query(SyncError).order_by(SyncError.created_at.desc()).limit(limit).all()

    def get_recent_workflow_executions(self, limit: int = 5):
        return self.db.query(WorkflowExecution).order_by(WorkflowExecution.executed_at.desc()).limit(limit).all()

    def get_email_volume_series(self):
        query = text("""
            SELECT to_char(date_trunc('hour', received_at), 'HH24:00') as time_slot,
                   COUNT(*) as incoming,
                   0 as automated
            FROM emails
            WHERE received_at >= NOW() - INTERVAL '24 hours'
            GROUP BY time_slot
            ORDER BY time_slot ASC
        """)
        result = self.db.execute(query).fetchall()
        
        # If there is no data, provide a baseline to keep the UI from looking broken
        if not result:
            return [{"time": "00:00", "incoming": 0, "automated": 0}]
            
        return [{"time": row[0], "incoming": row[1], "automated": row[2]} for row in result]


from sqlalchemy.orm import Session
from app.core.repository import BaseRepository
from app.models.workflow import WorkflowExecution
from app.schemas.workflow_execution import WorkflowExecutionCreate, WorkflowExecutionUpdate

class WorkflowExecutionRepository(BaseRepository[WorkflowExecution, WorkflowExecutionCreate, WorkflowExecutionUpdate]):
    def __init__(self, db: Session):
        super().__init__(WorkflowExecution, db)
        
    # No custom methods required at this time.
    # BaseRepository already provides create(), update(), get(), list(), and delete().

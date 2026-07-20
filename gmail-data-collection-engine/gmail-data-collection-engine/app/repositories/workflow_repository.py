from typing import Optional
from sqlalchemy.orm import Session, Query
from app.core.repository import BaseRepository
from app.models.workflow import Workflow
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate

class WorkflowRepository(BaseRepository[Workflow, WorkflowCreate, WorkflowUpdate]):
    def __init__(self, db: Session):
        super().__init__(Workflow, db)

    def get_query(self, status: Optional[str] = None, search: Optional[str] = None) -> Query:
        """
        Builds an SQLAlchemy query for workflows based on optional filters.
        This is passed to the Pagination utility in the Service layer.
        """
        query = self.db.query(self.model)
        
        if status == 'active':
            query = query.filter(self.model.is_active == True)
        elif status == 'disabled':
            query = query.filter(self.model.is_active == False)
            
        if search:
            query = query.filter(self.model.name.ilike(f"%{search}%"))
            
        # Default sort: newest first
        query = query.order_by(self.model.created_at.desc())
        
        return query

    def get_by_name(self, name: str, mailbox_account_id: str) -> Optional[Workflow]:
        """
        Fetches a workflow by exact name for a specific mailbox.
        Useful for checking duplicates during creation.
        """
        return self.db.query(self.model).filter(
            self.model.name == name,
            self.model.mailbox_account_id == mailbox_account_id
        ).first()

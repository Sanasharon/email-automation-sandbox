from typing import Optional, Any
from sqlalchemy.orm import Session
from app.core.service import BaseService
from app.core.exceptions import AppException
from app.repositories.workflow_repository import WorkflowRepository
from app.models.mailbox_account import MailboxAccount
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate
from app.common.pagination import paginate_query, PaginatedResponse

class WorkflowService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.repository = WorkflowRepository(db)

    def get_workflows(self, status: Optional[str], search: Optional[str], page: int, page_size: int) -> PaginatedResponse:
        query = self.repository.get_query(status=status, search=search)
        items, meta = paginate_query(query, page, page_size)
        return PaginatedResponse(data=items, meta=meta)

    def _validate_workflow_json(self, trigger_conditions: dict, actions_json: dict):
        if trigger_conditions:
            operator = trigger_conditions.get("operator")
            self.validate_or_fail(operator in ["AND", "OR"], "Trigger operator must be 'AND' or 'OR'")
            
            rules = trigger_conditions.get("rules", [])
            self.validate_or_fail(isinstance(rules, list) and len(rules) > 0, "Trigger must contain at least one rule")
            
            valid_fields = ["subject", "sender", "recipient", "has_attachment", "label", "category"]
            valid_operators = ["contains", "equals", "starts_with", "ends_with"]
            for rule in rules:
                field = rule.get("field")
                op = rule.get("operator")
                val = rule.get("value")
                self.validate_or_fail(field in valid_fields, f"Invalid rule field: {field}")
                self.validate_or_fail(op in valid_operators, f"Invalid rule operator: {op}")
                self.validate_or_fail(val is not None and str(val).strip() != "", "Rule value cannot be empty")
                
                # Check category validation constraint if field is category
                if field == "category":
                    valid_cats = ["Billing Complaint", "Technical Support Request", "Refund Request", "General Inquiry", "Internal Escalation", "any"]
                    self.validate_or_fail(val in valid_cats or val == "", f"Invalid category: {val}")

        if actions_json:
            actions = actions_json.get("actions", [])
            self.validate_or_fail(isinstance(actions, list) and len(actions) > 0, "At least one action is required")
            
            valid_actions = ["add_label", "mark_important", "archive", "move_to_category", "log_execution"]
            for action in actions:
                act_type = action.get("type")
                self.validate_or_fail(act_type in valid_actions, f"Invalid action type: {act_type}")

    def get_workflow(self, workflow_id: str) -> Any:
        workflow = self.repository.get(workflow_id)
        if not workflow:
            raise AppException(message="Workflow not found", code="NOT_FOUND", status_code=404)
        return workflow

    def create_workflow(self, obj_in: WorkflowCreate) -> Any:
        def _create():
            mailbox = self.db.query(MailboxAccount).filter(MailboxAccount.id == obj_in.mailbox_account_id).first()
            if not mailbox:
                raise AppException(message="Mailbox account not found", code="NOT_FOUND", status_code=404)
            
            duplicate = self.repository.get_by_name(obj_in.name, str(obj_in.mailbox_account_id))
            self.validate_or_fail(duplicate is None, f"Workflow '{obj_in.name}' already exists.")
            
            self._validate_workflow_json(obj_in.trigger_conditions_json, obj_in.actions_json)
            
            # Basic validation for destination_team in description
            if obj_in.description and "Target Team:" in obj_in.description:
                team = obj_in.description.replace("Target Team:", "").strip()
                self.validate_or_fail(len(team) > 0, "Destination team cannot be empty if specified")

            return self.repository.create(obj_in)
        return self.execute_in_transaction(_create)

    def update_workflow(self, workflow_id: str, obj_in: WorkflowUpdate) -> Any:
        def _update():
            workflow = self.get_workflow(workflow_id)
            
            if obj_in.name and obj_in.name != workflow.name:
                duplicate = self.repository.get_by_name(obj_in.name, str(workflow.mailbox_account_id))
                self.validate_or_fail(duplicate is None, f"Workflow '{obj_in.name}' already exists.")

            if obj_in.trigger_conditions_json or obj_in.actions_json:
                triggers = obj_in.trigger_conditions_json if obj_in.trigger_conditions_json is not None else workflow.trigger_conditions_json
                actions = obj_in.actions_json if obj_in.actions_json is not None else workflow.actions_json
                self._validate_workflow_json(triggers, actions)
                
            if obj_in.description and "Target Team:" in obj_in.description:
                team = obj_in.description.replace("Target Team:", "").strip()
                self.validate_or_fail(len(team) > 0, "Destination team cannot be empty if specified")

            return self.repository.update(workflow, obj_in)
        return self.execute_in_transaction(_update)

    def delete_workflow(self, workflow_id: str) -> bool:
        def _delete():
            self.get_workflow(workflow_id)
            return self.repository.delete(workflow_id)
        return self.execute_in_transaction(_delete)

    def toggle_state(self, workflow_id: str, action: str) -> Any:
        def _toggle():
            self.validate_or_fail(action in ["enable", "disable"], "Action must be 'enable' or 'disable'")
            workflow = self.get_workflow(workflow_id)
            is_active = (action == "enable")
            return self.repository.update(workflow, {"is_active": is_active})
        return self.execute_in_transaction(_toggle)

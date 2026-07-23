from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.prompt_template import PromptTemplate
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/prompt-templates", tags=["prompt-templates"], dependencies=[Depends(get_current_user)])

class PromptTemplateCreate(BaseModel):
    name: str
    purpose: Optional[str] = None
    prompt_content: str
    variables_json: Optional[str] = "[]"

class PromptTemplateResponse(BaseModel):
    id: str
    name: str
    purpose: Optional[str] = None
    prompt_content: str
    variables_json: Optional[str] = "[]"
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[PromptTemplateResponse])
def list_prompt_templates(db: Session = Depends(get_db)):
    templates = db.query(PromptTemplate).filter(PromptTemplate.is_active == True).order_by(PromptTemplate.created_at.desc()).all()
    return [
        PromptTemplateResponse(
            id=str(t.id),
            name=t.name,
            purpose=t.purpose,
            prompt_content=t.prompt_content,
            variables_json=t.variables_json,
            is_active=t.is_active,
            created_at=t.created_at
        ) for t in templates
    ]

@router.post("/", response_model=PromptTemplateResponse)
def create_prompt_template(
    payload: PromptTemplateCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    template = PromptTemplate(
        name=payload.name,
        purpose=payload.purpose,
        prompt_content=payload.prompt_content,
        variables_json=payload.variables_json,
        user_id=current_user.get("id")
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return PromptTemplateResponse(
        id=str(template.id),
        name=template.name,
        purpose=template.purpose,
        prompt_content=template.prompt_content,
        variables_json=template.variables_json,
        is_active=template.is_active,
        created_at=template.created_at
    )

@router.delete("/{template_id}")
def delete_prompt_template(template_id: str, db: Session = Depends(get_db)):
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    template.is_active = False
    db.commit()
    return {"message": "Prompt template deleted successfully"}

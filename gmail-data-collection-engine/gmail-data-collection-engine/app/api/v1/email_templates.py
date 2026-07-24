from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.email_template import EmailTemplate
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/email-templates", tags=["email-templates"], dependencies=[Depends(get_current_user)])


class EmailTemplateCreate(BaseModel):
    name: str
    subject: Optional[str] = None
    body_html: str
    body_text: Optional[str] = None
    category: Optional[str] = None


class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class EmailTemplateResponse(BaseModel):
    id: str
    name: str
    subject: Optional[str] = None
    body_html: str
    body_text: Optional[str] = None
    category: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[EmailTemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    templates = db.query(EmailTemplate).filter(EmailTemplate.is_active == True).order_by(EmailTemplate.created_at.desc()).all()
    return [_to_response(t) for t in templates]


@router.post("/", response_model=EmailTemplateResponse)
def create_template(payload: EmailTemplateCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    template = EmailTemplate(
        name=payload.name,
        subject=payload.subject,
        body_html=payload.body_html,
        body_text=payload.body_text,
        category=payload.category,
        user_id=current_user.get("id")
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return _to_response(template)


@router.get("/{template_id}", response_model=EmailTemplateResponse)
def get_template(template_id: str, db: Session = Depends(get_db)):
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Email template not found")
    return _to_response(template)


@router.put("/{template_id}", response_model=EmailTemplateResponse)
def update_template(template_id: str, payload: EmailTemplateUpdate, db: Session = Depends(get_db)):
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Email template not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(template, key, value)
    db.commit()
    db.refresh(template)
    return _to_response(template)


@router.delete("/{template_id}")
def delete_template(template_id: str, db: Session = Depends(get_db)):
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Email template not found")
    template.is_active = False
    db.commit()
    return {"success": True, "message": "Email template deleted"}


def _to_response(t) -> EmailTemplateResponse:
    return EmailTemplateResponse(
        id=str(t.id),
        name=t.name,
        subject=t.subject,
        body_html=t.body_html,
        body_text=t.body_text,
        category=t.category,
        is_active=t.is_active,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )

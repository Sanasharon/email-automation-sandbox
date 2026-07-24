from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.services.ai_provider_service import AIProviderService
from app.core.responses import success_response

router = APIRouter(prefix="/ai-providers", tags=["ai-providers"], dependencies=[Depends(get_current_user)])


class AIProviderCreate(BaseModel):
    name: str
    provider_type: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_enabled: Optional[bool] = True
    is_primary: Optional[bool] = False
    priority: Optional[int] = 0
    max_tokens: Optional[int] = 800
    temperature: Optional[float] = 0.7
    timeout: Optional[int] = 30
    retry_count: Optional[int] = 3


class AIProviderUpdate(BaseModel):
    name: Optional[str] = None
    provider_type: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_enabled: Optional[bool] = None
    is_primary: Optional[bool] = None
    priority: Optional[int] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    timeout: Optional[int] = None
    retry_count: Optional[int] = None


class AIProviderResponse(BaseModel):
    id: str
    name: str
    provider_type: str
    model: str
    api_key_set: bool
    base_url: Optional[str] = None
    is_enabled: bool
    is_primary: bool
    priority: int
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    timeout: Optional[int] = None
    retry_count: Optional[int] = None
    status: str
    last_tested_at: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AIProviderResponse])
def list_providers(db: Session = Depends(get_db)):
    service = AIProviderService(db)
    providers = service.get_providers()
    return [_to_response(p) for p in providers]


@router.post("/", response_model=AIProviderResponse)
def create_provider(payload: AIProviderCreate, db: Session = Depends(get_db)):
    service = AIProviderService(db)
    data = payload.model_dump()
    if data.get("api_key"):
        data["api_key_encrypted"] = data.pop("api_key")
    else:
        data.pop("api_key", None)
    data["default_model"] = data.get("model", "")
    provider = service.create_provider(data)
    return _to_response(provider)


@router.get("/{provider_id}", response_model=AIProviderResponse)
def get_provider(provider_id: str, db: Session = Depends(get_db)):
    service = AIProviderService(db)
    provider = service.get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return _to_response(provider)


@router.put("/{provider_id}", response_model=AIProviderResponse)
def update_provider(provider_id: str, payload: AIProviderUpdate, db: Session = Depends(get_db)):
    service = AIProviderService(db)
    data = payload.model_dump(exclude_unset=True)
    if data.get("api_key"):
        data["api_key_encrypted"] = data.pop("api_key")
    else:
        data.pop("api_key", None)
    if "model" in data:
        data["default_model"] = data["model"]
    provider = service.update_provider(provider_id, data)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return _to_response(provider)


@router.delete("/{provider_id}")
def delete_provider(provider_id: str, db: Session = Depends(get_db)):
    service = AIProviderService(db)
    if not service.delete_provider(provider_id):
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"success": True, "message": "Provider deleted"}


@router.post("/{provider_id}/test")
def test_provider(provider_id: str, db: Session = Depends(get_db)):
    service = AIProviderService(db)
    result = service.test_provider(provider_id)
    if not result["success"] and "not found" in result.get("error", "").lower():
        raise HTTPException(status_code=404, detail="Provider not found")
    return success_response(data=result)


def _to_response(p) -> AIProviderResponse:
    model_name = getattr(p, 'model', None) or getattr(p, 'default_model', None) or 'unknown'
    api_key_val = getattr(p, 'api_key_encrypted', None) or getattr(p, 'api_key', None)
    return AIProviderResponse(
        id=str(p.id),
        name=p.name,
        provider_type=p.provider_type,
        model=model_name,
        api_key_set=bool(api_key_val),
        base_url=p.base_url,
        is_enabled=p.is_enabled,
        is_primary=getattr(p, 'is_primary', False) or False,
        priority=p.priority,
        max_tokens=getattr(p, 'max_tokens', None),
        temperature=getattr(p, 'temperature', None),
        timeout=getattr(p, 'timeout', 30),
        retry_count=getattr(p, 'retry_count', 3),
        status=p.status,
        last_tested_at=p.last_tested_at,
        last_error=getattr(p, 'last_error', None),
        created_at=p.created_at,
        updated_at=p.updated_at,
    )

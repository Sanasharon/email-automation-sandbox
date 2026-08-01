# app/schemas/category.py
from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    active: Optional[bool] = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    active: Optional[bool]

class CategoryResponse(CategoryBase):
    id: UUID4
    created_by: Optional[UUID4]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EmailCategoryResponse(BaseModel):
    category_id: Optional[UUID4]
    category_name: str
    confidence: float
    assigned_by: Optional[UUID4]
    assigned_at: datetime
    corrected: bool

    class Config:
        from_attributes = True
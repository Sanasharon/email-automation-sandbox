from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator

class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    permissions: List[str] = Field(default_factory=list)

    @validator('permissions', each_item=True)
    def validate_permission(cls, v: str) -> str:
        # Simple validation: must be known permission string
        if not isinstance(v, str) or not v:
            raise ValueError('Invalid permission')
        return v

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str]
    permissions: Optional[List[str]]

class RoleOut(RoleBase):
    id: UUID
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True

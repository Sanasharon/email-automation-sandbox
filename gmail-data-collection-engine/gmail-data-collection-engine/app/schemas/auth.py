from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str = "Viewer"
    permissions: List[str] = []

class LoginResponse(BaseModel):
    success: bool = True
    token: str
    user: UserResponse

class MeResponse(BaseModel):
    success: bool = True
    user: UserResponse

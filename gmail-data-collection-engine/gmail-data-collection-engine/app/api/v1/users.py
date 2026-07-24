"""
Users Management API — CRUD for user accounts.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from passlib.context import CryptContext

from app.db.session import get_db
from app.models.user import User, UserRole
from app.auth.dependencies import get_current_user, require_permission

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role_id: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    role_id: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


def _to_response(user, role=None) -> UserResponse:
    if role is None and user.role_id:
        role_name = "Viewer"
    else:
        role_name = role.name if role else "Viewer"
    return UserResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        role=role_name,
        role_id=str(user.role_id) if user.role_id else "",
        is_active=user.is_active,
        last_login=user.last_login,
        created_at=user.created_at,
    )


@router.get("/")
def list_users(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(User).filter(User.is_deleted == False)
    if search:
        query = query.filter(
            User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
        )
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result = []
    for u in users:
        role = db.query(UserRole).filter(UserRole.id == u.role_id).first() if u.role_id else None
        result.append(_to_response(u, role))
    
    return {
        "success": True,
        "data": result,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    }


@router.post("/")
def create_user(
    payload: UserCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == payload.email, User.is_deleted == False).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    role_id = payload.role_id
    if not role_id:
        viewer_role = db.query(UserRole).filter(UserRole.name == "Viewer").first()
        role_id = str(viewer_role.id) if viewer_role else None

    user = User(
        email=payload.email,
        name=payload.name,
        hashed_password=pwd_context.hash(payload.password),
        role_id=role_id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    role = db.query(UserRole).filter(UserRole.id == user.role_id).first() if user.role_id else None
    return {"success": True, "user": _to_response(user, role)}


@router.put("/{user_id}")
def update_user(
    user_id: str,
    payload: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        existing = db.query(User).filter(User.email == payload.email, User.id != user_id, User.is_deleted == False).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = payload.email
    if payload.role_id is not None:
        user.role_id = payload.role_id
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password:
        user.hashed_password = pwd_context.hash(payload.password)
    
    db.commit()
    db.refresh(user)
    role = db.query(UserRole).filter(UserRole.id == user.role_id).first() if user.role_id else None
    return {"success": True, "user": _to_response(user, role)}


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if str(user.id) == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    user.is_deleted = True
    user.is_active = False
    db.commit()
    return {"success": True, "message": "User deleted"}

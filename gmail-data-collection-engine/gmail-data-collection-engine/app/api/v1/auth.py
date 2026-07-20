from fastapi import APIRouter, Depends, HTTPException
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.config import settings
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, LoginResponse, MeResponse
from app.auth.dependencies import get_current_user, require_permission

router = APIRouter(prefix="/auth", tags=["Auth"])

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")

@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    try:
        # Check password against hashed_password
        if not bcrypt.checkpw(req.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            raise ValueError()
    except:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
        
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    role = db.query(UserRole).filter(UserRole.id == user.role_id).first()
    role_name = role.name if role else "Viewer"
    permissions = role.permissions_json if role else []
    
    expires_delta = timedelta(minutes=settings.jwt_expires_in_minutes)
    token = create_access_token({"id": str(user.id), "role": role_name}, expires_delta)
    
    formatted_user = {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "role": role_name,
        "permissions": permissions
    }
    
    return {"success": True, "token": token, "user": formatted_user}

@router.post("/logout")
def logout():
    return {"success": True, "message": "Logged out successfully"}

@router.get("/me", response_model=MeResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return {"success": True, "user": current_user}

@router.get("/test-protected")
def test_protected(current_user: dict = Depends(require_permission('super_secret_action'))):
    """Simple test endpoint to verify the auth layer correctly rejects unauthenticated requests."""
    return {"success": True, "message": f"Hello {current_user['name']}, you are authenticated!"}

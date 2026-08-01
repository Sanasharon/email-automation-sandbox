# app/api/v1/priorities.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict
from app.services.priority_service import classify_text_priority, classify_email_priority
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
import datetime

router = APIRouter(prefix="/priorities", tags=["priorities"])

@router.post("/emails/{email_id}/classify", response_model=Dict[str, str])
def classify_email_endpoint(email_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Classify priority for a specific email and persist results.
    Returns {"priority": "<High|Medium|Low>", "confidence": "<float>"}
    """
    res = classify_email_priority(email_id, db=db, persist=True)
    return {"priority": res.get("priority"), "confidence": str(res.get("confidence"))}

@router.post("/classify", response_model=Dict[str, str])
def classify_text_endpoint(payload: Dict[str, str] = Body(..., example={"text":"Please help - invoice is overdue"}), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Classify the priority for arbitrary text (no persistence).
    """
    text = payload.get("text", "")
    res = classify_text_priority(text, db=db)
    return {"priority": res.get("priority"), "confidence": str(res.get("confidence"))}
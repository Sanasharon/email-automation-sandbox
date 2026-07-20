from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.core.responses import success_response, error_response
import time

router = APIRouter(prefix="/health", tags=["System Health"])

@router.get("")
def health_check():
    return success_response(data={"status": "up"}, message="System is operational")

@router.get("/database")
def database_health(db: Session = Depends(get_db)):
    start_time = time.time()
    try:
        db.execute(text("SELECT 1"))
        latency = (time.time() - start_time) * 1000
        return success_response(
            data={"status": "connected", "latency_ms": round(latency, 2)},
            message="Database connection successful"
        )
    except Exception as e:
        return error_response(
            code="DB_CONNECTION_FAILED",
            message="Failed to connect to the database",
            details={"error": str(e)}
        )

@router.get("/storage")
def storage_health():
    # Placeholder for Supabase Storage check
    return success_response(data={"status": "up"}, message="Storage is operational")

@router.get("/system")
def system_health():
    # Placeholder for system stats (CPU, RAM)
    return success_response(data={"status": "up", "version": "v1.0.0"})

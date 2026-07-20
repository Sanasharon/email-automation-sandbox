from fastapi import APIRouter
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.health import router as health_router
from app.api.v1.workflows import router as workflows_router
from app.api.v1.automation import router as automation_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.auth import router as auth_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(health_router)
api_v1_router.include_router(workflows_router)
api_v1_router.include_router(automation_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(auth_router)

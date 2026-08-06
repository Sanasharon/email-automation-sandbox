from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, auth, mailboxes, sync, emails, dashboard
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.logging import StructuredLoggingMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware
from app.core.exceptions import global_exception_handler
from app.config import settings
import logging

from app.scheduler.startup import lifespan

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Utservio Gmail Communication Data Collection Engine",
    description="Secure backend service for Gmail email synchronization, attachment processing, and Supabase data storage.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_exception_handler(Exception, global_exception_handler)

# --- CORRECT MIDDLEWARE ORDER ---
# CORSMiddleware must be added FIRST so it executes LAST (wrapping inner layers and rate limiters)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# --- Core API routers ---
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(mailboxes.router, prefix="/api/v1")
app.include_router(sync.router)
app.include_router(emails.router)

# --- Dashboard / Review routers ---
app.include_router(dashboard.router)
from app.api.admin import admin_router
app.include_router(admin_router)

# --- Sprint 4 API v1 routers (includes users, roles, workflows, AI, templates, logs) ---
from app.api.v1 import api_v1_router
app.include_router(api_v1_router)

# --- Analytics router registration ---
try:
    from app.api.v1.analytics import router as analytics_router
    ANALYTICS_AVAILABLE = True
except Exception:
    ANALYTICS_AVAILABLE = False
    analytics_router = None

if ANALYTICS_AVAILABLE and analytics_router:
    app.include_router(analytics_router)

# start scheduler in startup
@app.on_event("startup")
async def startup_event():
    try:
        from app.scheduler import scheduler, register_jobs
        register_jobs()
        if not scheduler.running:
            scheduler.start()
    except Exception:
        import logging
        logging.exception("Failed to start scheduler")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        from app.scheduler import scheduler
        scheduler.shutdown(wait=False)
    except Exception:
        import logging
        logging.exception("Failed to shutdown scheduler")
"""
FastAPI Lifespan Startup & Shutdown Management.
Hooks APScheduler initialization directly into the FastAPI application lifecycle.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.scheduler.scheduler_service import scheduler_service

logger = logging.getLogger("scheduler_startup")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Context Manager.
    Starts background services on app boot and gracefully cleans up resources on shutdown.
    """
    logger.info("[LIFESPAN] Starting FastAPI application services...")
    try:
        scheduler_service.start()
    except Exception as e:
        logger.error(f"[LIFESPAN] Failed to start APScheduler during app boot: {e}")

    yield

    logger.info("[LIFESPAN] Shutting down FastAPI application services...")
    try:
        scheduler_service.shutdown()
    except Exception as e:
        logger.error(f"[LIFESPAN] Failed to shutdown APScheduler: {e}")

# app/scheduler/__init__.py
"""
Package exports for app.scheduler.

Exports:
- scheduler: the AsyncIOScheduler instance managed by SchedulerService
- register_jobs: convenience shim that initializes/registers jobs via SchedulerService.start()
- scheduler_service: the SchedulerService singleton (optional export)
- lifespan: FastAPI lifespan context manager (if present)
"""

import logging
logger = logging.getLogger(__name__)

# Try to import the canonical SchedulerService and lifespan; fail gracefully if something breaks.
scheduler = None
register_jobs = lambda: logger.debug("register_jobs noop (scheduler not available)")
scheduler_service = None
lifespan = None

try:
    from .scheduler_service import scheduler_service as _scheduler_service  # SchedulerService singleton
    scheduler_service = _scheduler_service
    # scheduler is the underlying AsyncIOScheduler instance used by the service
    scheduler = getattr(scheduler_service, "scheduler", None)

    # register_jobs delegates to scheduler_service.start which registers jobs and starts scheduler
    def register_jobs():
        try:
            scheduler_service.start()
        except Exception as e:
            logger.exception("Failed to start/register jobs via scheduler_service: %s", e)

    logger.debug("Exported scheduler and register_jobs via scheduler_service.")
except Exception as e:
    logger.debug("Could not import scheduler_service: %s", e)

# Try to import lifespan helper (optional)
try:
    from .startup import lifespan as _lifespan  # asynccontextmanager for FastAPI lifespan
    lifespan = _lifespan
    logger.debug("Exported lifespan from app.scheduler.startup")
except Exception:
    # Not fatal; lifespan is optional
    pass

__all__ = ["scheduler", "register_jobs", "scheduler_service", "lifespan"]
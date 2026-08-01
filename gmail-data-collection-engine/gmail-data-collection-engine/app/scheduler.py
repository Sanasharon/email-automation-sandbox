# app/scheduler.py
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.jobs.analytics_jobs import run_analytics_aggregation

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

def register_jobs():
    # register analytics aggregation every 5 minutes
    scheduler.add_job(
        run_analytics_aggregation,
        "interval",
        minutes=5,
        id="analytics_aggregation",
        replace_existing=True,
        coalesce=True,
        max_instances=1,
        misfire_grace_time=300,
    )
    logger.info("Analytics aggregation job registered")
# app/jobs/analytics_jobs.py
import logging
from app.services.analytics_service import compute_summary, upsert_cache, CACHE_KEYS
from sqlalchemy.orm import Session
from app.db.session import SessionLocal  # or import how you create sessions

logger = logging.getLogger(__name__)

def run_analytics_aggregation():
    """
    Aggregation job: compute summary and persist to analytics_cache.
    Use an independent DB session to avoid interfering with request sessions.
    """
    db: Session = SessionLocal()
    try:
        summary = compute_summary(db)
        upsert_cache(db, CACHE_KEYS["summary"], summary)
        logger.info("Analytics aggregation: cached summary")
    except Exception:
        logger.exception("Analytics aggregation job failed")
    finally:
        db.close()
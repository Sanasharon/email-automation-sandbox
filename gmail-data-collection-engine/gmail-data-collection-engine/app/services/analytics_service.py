# app/services/analytics_service.py
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from app.models.email import Email
from app.models.category import Category
from app.models.email_category import EmailCategory
from app.models.ai_task import AiTask
from app.models.analytics_cache import AnalyticsCache

CACHE_KEYS = {
    "summary": "analytics_summary",
}

# Compute the analytics summary from DB
def compute_summary(db: Session) -> Dict[str, Any]:
    # Category counts
    cat_q = (
        db.query(Category.name.label("category_name"), func.count(EmailCategory.email_id).label("count"))
        .join(EmailCategory, EmailCategory.category_id == Category.id)
        .group_by(Category.name)
        .order_by(func.count(EmailCategory.email_id).desc())
    )
    category_counts = [{"category_name": r.category_name, "count": int(r.count)} for r in cat_q]

    # Priority counts
    pr_q = db.query(Email.priority, func.count(Email.id).label("count")).group_by(Email.priority).order_by(func.count(Email.id).desc())
    priority_counts = [{"priority": r.priority or "Unknown", "count": int(r.count)} for r in pr_q]

    total_emails = int(db.query(func.count(Email.id)).scalar() or 0)
    processed_count = int(db.query(func.count(Email.id)).filter(Email.ai_processing_status == "completed").scalar() or 0)
    processing_backlog = int(db.query(func.count(Email.id)).filter(Email.ai_processing_status != "completed").scalar() or 0)

    pending_tasks = int(db.query(func.count(AiTask.id)).filter(AiTask.status.in_(["pending", "scheduled", "running"])).scalar() or 0)
    failed_tasks_24h = int(db.query(func.count(AiTask.id)).filter(AiTask.status == "failed", AiTask.updated_at >= datetime.utcnow() - timedelta(days=1)).scalar() or 0)

    return {
        "category_counts": category_counts,
        "priority_counts": priority_counts,
        "totals": {
            "total_emails": total_emails,
            "processed_count": processed_count,
            "processing_backlog": processing_backlog,
        },
        "task_summary": {
            "pending_tasks": pending_tasks,
            "failed_tasks_last_24h": failed_tasks_24h,
        },
    }

# Compute daily trends for last `days`
def compute_daily_trends(db: Session, days: int = 30) -> Dict[str, Any]:
    since = datetime.utcnow() - timedelta(days=days)
    q = (
        db.query(func.date_trunc("day", Email.received_at).label("day"), func.count(Email.id).label("count"))
        .filter(Email.received_at >= since)
        .group_by(func.date_trunc("day", Email.received_at))
        .order_by(func.date_trunc("day", Email.received_at))
    )
    data = [{"day": r.day.strftime("%Y-%m-%d"), "count": int(r.count)} for r in q]
    return {"days": days, "data": data}

# Compute processing time stats
def compute_processing_times(db: Session, days: int = 30) -> Dict[str, Any]:
    since = datetime.utcnow() - timedelta(days=days)
    stmt = text(
        """
        SELECT
          avg(EXTRACT(epoch FROM (ai_processed_at - created_at))) as avg_seconds,
          percentile_disc(0.5) WITHIN GROUP (ORDER BY EXTRACT(epoch FROM (ai_processed_at - created_at))) as median_seconds,
          percentile_disc(0.9) WITHIN GROUP (ORDER BY EXTRACT(epoch FROM (ai_processed_at - created_at))) as p90_seconds,
          count(*) as processed_count
        FROM emails
        WHERE ai_processed_at IS NOT NULL AND ai_processed_at >= :since
        """
    )
    res = db.execute(stmt, {"since": since}).mappings().first()
    if res is None or res["processed_count"] == 0:
        return {"avg_seconds": None, "median_seconds": None, "p90_seconds": None, "processed_count": 0}
    return {
        "avg_seconds": float(res["avg_seconds"]) if res["avg_seconds"] is not None else None,
        "median_seconds": float(res["median_seconds"]) if res["median_seconds"] is not None else None,
        "p90_seconds": float(res["p90_seconds"]) if res["p90_seconds"] is not None else None,
        "processed_count": int(res["processed_count"]),
    }

# Cache helpers: upsert into analytics_cache
def upsert_cache(db: Session, key: str, payload: Any) -> None:
    existing = db.query(AnalyticsCache).filter(AnalyticsCache.key == key).first()
    if existing:
        existing.payload = payload
    else:
        obj = AnalyticsCache(key=key, payload=payload)
        db.add(obj)
    db.commit()

def read_cache(db: Session, key: str) -> Optional[Any]:
    row = db.query(AnalyticsCache).filter(AnalyticsCache.key == key).first()
    return row.payload if row else None
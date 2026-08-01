from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, cast, Date
from datetime import datetime, timedelta, timezone
from app.db.session import get_db
from app.models.email import Email
from app.models.mailbox_account import MailboxAccount
from app.auth.dependencies import get_current_user
from app.core.responses import success_response

router = APIRouter(prefix="/analytics", tags=["Analytics"], dependencies=[Depends(get_current_user)])


def _scoped_query(db: Session, current_user: dict):
    user_id = current_user["id"]
    mailbox_ids = [
        m.id for m in db.query(MailboxAccount).filter(
            or_(MailboxAccount.user_id == user_id, MailboxAccount.user_id == None)
        ).all()
    ]
    query = db.query(Email)
    if mailbox_ids:
        query = query.filter(Email.mailbox_account_id.in_(mailbox_ids))
    return query


@router.get("/summary", summary="Get analytics summary: category counts, priority counts, daily trend, processing time")
def get_analytics_summary(
    request: Request,
    days: int = Query(7, ge=1, le=90),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    base = _scoped_query(db, current_user)

    total_emails = base.count()

    category_rows = base.with_entities(Email.category, func.count(Email.id)).group_by(Email.category).all()
    category_counts = {(cat or "Uncategorized"): count for cat, count in category_rows}

    priority_rows = base.with_entities(Email.priority, func.count(Email.id)).group_by(Email.priority).all()
    priority_counts = {(p or "unset"): count for p, count in priority_rows}
    high_count = priority_counts.get("high", 0)
    high_priority_pct = round((high_count / total_emails) * 100, 1) if total_emails else 0.0

    since = datetime.now(timezone.utc) - timedelta(days=days)
    trend_rows = (
        base.filter(Email.received_at != None, Email.received_at >= since)
        .with_entities(cast(Email.received_at, Date).label("day"), func.count(Email.id))
        .group_by("day")
        .order_by("day")
        .all()
    )
    daily_trend = [{"date": day.isoformat(), "count": count} for day, count in trend_rows]

    avg_seconds = (
        base.filter(Email.processed_at != None)
        .with_entities(func.avg(func.extract("epoch", Email.processed_at - Email.created_at)))
        .scalar()
    )
    avg_processing_time_seconds = round(float(avg_seconds), 1) if avg_seconds else None

    processing_trend_rows = (
        base.filter(Email.processed_at != None, Email.processed_at >= since)
        .with_entities(
            cast(Email.processed_at, Date).label("day"),
            func.avg(func.extract("epoch", Email.processed_at - Email.created_at)),
        )
        .group_by("day")
        .order_by("day")
        .all()
    )
    processing_time_trend = [
        {"date": day.isoformat(), "avg_seconds": round(float(avg), 1)} for day, avg in processing_trend_rows
    ]

    return success_response(
        data={
            "emails_processed": total_emails,
            "avg_processing_time_seconds": avg_processing_time_seconds,
            "high_priority_pct": high_priority_pct,
            "categories_tracked": len(category_counts),
            "category_counts": category_counts,
            "priority_counts": priority_counts,
            "daily_trend": daily_trend,
            "processing_time_trend": processing_time_trend,
        },
        request_id=request.state.request_id,
    )

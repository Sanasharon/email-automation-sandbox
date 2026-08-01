from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session, load_only
from sqlalchemy import func, or_, case
from app.db.session import get_db
from app.models.email import Email
from app.models.mailbox_account import MailboxAccount
from app.auth.dependencies import get_current_user
from app.core.responses import success_response

router = APIRouter(prefix="/categories", tags=["Categories & Priority"], dependencies=[Depends(get_current_user)])

PRIORITY_RANK = case(
    (Email.priority == "high", 3),
    (Email.priority == "medium", 2),
    (Email.priority == "low", 1),
    else_=0,
)


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


@router.get("/counts", summary="Get email counts per category")
def get_category_counts(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = _scoped_query(db, current_user)
    rows = query.with_entities(Email.category, func.count(Email.id)).group_by(Email.category).all()
    counts = {(cat or "Uncategorized"): count for cat, count in rows}
    total = sum(counts.values())
    return success_response(data={"total": total, "categories": counts}, request_id=request.state.request_id)


@router.get("/", summary="List emails filtered by category, sorted by priority")
def list_by_category(
    request: Request,
    category: str = Query("All"),
    search: str = Query(""),
    sort: str = Query("desc", regex="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = _scoped_query(db, current_user)

    if category and category != "All":
        query = query.filter(Email.category == category)

    if search:
        term = f"%{search}%"
        query = query.filter(or_(Email.subject.ilike(term), Email.sender_email.ilike(term)))

    total = query.count()

    order = PRIORITY_RANK.desc() if sort == "desc" else PRIORITY_RANK.asc()
    emails = query.options(
        load_only(
            Email.id, Email.category, Email.priority, Email.subject,
            Email.sender_email, Email.received_at, Email.processing_status,
        )
    ).order_by(order, Email.received_at.desc().nulls_last()).offset(skip).limit(limit).all()

    data = [
        {
            "id": str(e.id),
            "category": e.category or "Uncategorized",
            "priority": e.priority or "unset",
            "subject": e.subject,
            "sender": e.sender_email,
            "received_at": e.received_at.isoformat() if e.received_at else None,
            "status": e.processing_status,
        }
        for e in emails
    ]

    return success_response(
        data={"data": data, "total": total, "skip": skip, "limit": limit},
        request_id=request.state.request_id,
    )

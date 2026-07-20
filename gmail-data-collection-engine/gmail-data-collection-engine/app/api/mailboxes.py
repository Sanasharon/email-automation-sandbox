from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.mailbox_account import MailboxAccount

router = APIRouter(prefix="/mailboxes", tags=["mailboxes"])

@router.get("/")
def list_mailboxes(db: Session = Depends(get_db)):
    return db.query(MailboxAccount).all()

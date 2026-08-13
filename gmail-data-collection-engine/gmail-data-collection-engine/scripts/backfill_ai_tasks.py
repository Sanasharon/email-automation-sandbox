from app.db.session import SessionLocal
from app.models.email import Email
from app.services.ai_task_service import enqueue_task

db = SessionLocal()
emails = db.query(Email).filter(Email.ai_processing_status == "not_started").all()
print(f"Backfilling {len(emails)} email(s)...")
for email in emails:
    enqueue_task(db, task_type="classification", email_id=str(email.id))
    enqueue_task(db, task_type="priority", email_id=str(email.id))
db.close()
print("Done.")
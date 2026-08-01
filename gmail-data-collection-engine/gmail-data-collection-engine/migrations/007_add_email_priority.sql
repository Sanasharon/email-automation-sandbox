-- migrations/005_add_email_priority.sql
-- Add priority and priority_confidence columns to emails table

BEGIN;

ALTER TABLE emails
  ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'Medium';

ALTER TABLE emails
  ADD COLUMN IF NOT EXISTS priority_confidence DOUBLE PRECISION DEFAULT 0.0;

-- Add an index for priority queries
CREATE INDEX IF NOT EXISTS ix_emails_priority ON emails(priority);

COMMIT;
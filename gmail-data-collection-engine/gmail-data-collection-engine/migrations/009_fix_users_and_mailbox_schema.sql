-- Migration: 009_fix_users_and_mailbox_schema.sql
-- Add missing columns to users table matching app/models/user.py
BEGIN;

ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(255) NOT NULL DEFAULT 'User';
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_by UUID;
ALTER TABLE users ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;

-- Add helpful indexes on mailbox_accounts and emails if missing
CREATE INDEX IF NOT EXISTS ix_mailbox_account_identifier ON mailbox_accounts(account_identifier);
CREATE INDEX IF NOT EXISTS ix_emails_sender_email ON emails(sender_email);

COMMIT;

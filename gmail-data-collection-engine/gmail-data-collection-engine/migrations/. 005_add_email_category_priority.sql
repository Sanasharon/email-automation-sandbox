-- Add category and priority columns to emails table
ALTER TABLE public.emails
  ADD COLUMN IF NOT EXISTS category VARCHAR,
  ADD COLUMN IF NOT EXISTS priority VARCHAR;

-- Optional indexes if you will query by mailbox_account_id + category/priority
CREATE INDEX IF NOT EXISTS ix_email_account_category ON public.emails (mailbox_account_id, category);
CREATE INDEX IF NOT EXISTS ix_email_account_priority ON public.emails (mailbox_account_id, priority);
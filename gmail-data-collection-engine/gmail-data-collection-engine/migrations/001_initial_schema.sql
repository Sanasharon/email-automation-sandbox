-- Enable pgcrypto for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create reusable trigger function for updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Table: mailbox_accounts
CREATE TABLE mailbox_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR NOT NULL DEFAULT 'gmail',
    account_identifier VARCHAR NOT NULL,
    auth_mode VARCHAR NOT NULL DEFAULT 'desktop_oauth',
    last_history_id TEXT,
    last_sync_at TIMESTAMPTZ,
    sync_status VARCHAR NOT NULL DEFAULT 'connected',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_mailbox_account_sync_status CHECK (sync_status IN ('connected', 'syncing', 'error', 'disabled'))
);

CREATE UNIQUE INDEX uq_mailbox_provider_account_identifier ON mailbox_accounts (LOWER(provider), LOWER(account_identifier));

CREATE TRIGGER trg_mailbox_accounts_updated_at
BEFORE UPDATE ON mailbox_accounts
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Table: emails
CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mailbox_account_id UUID NOT NULL,
    provider_message_id VARCHAR NOT NULL,
    provider_thread_id VARCHAR,
    sender_email VARCHAR,
    to_recipients JSONB NOT NULL DEFAULT '[]'::jsonb,
    cc_recipients JSONB NOT NULL DEFAULT '[]'::jsonb,
    bcc_recipients JSONB NOT NULL DEFAULT '[]'::jsonb,
    subject TEXT,
    body_text TEXT,
    body_html TEXT,
    snippet TEXT,
    labels JSONB NOT NULL DEFAULT '[]'::jsonb,
    received_at TIMESTAMPTZ,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    has_attachments BOOLEAN NOT NULL DEFAULT FALSE,
    raw_email_json JSONB,
    processing_status VARCHAR NOT NULL DEFAULT 'collected',
    last_processing_error TEXT,
    processed_at TIMESTAMPTZ,
    ai_processing_status VARCHAR NOT NULL DEFAULT 'not_started',
    ai_processed_at TIMESTAMPTZ,
    record_status VARCHAR NOT NULL DEFAULT 'active',
    archived_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ,
    retention_category VARCHAR,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_emails_mailbox_account_id FOREIGN KEY (mailbox_account_id) REFERENCES mailbox_accounts (id) ON DELETE RESTRICT,
    CONSTRAINT uq_email_account_provider_msg_id UNIQUE (mailbox_account_id, provider_message_id),
    CONSTRAINT ck_email_processing_status CHECK (processing_status IN ('collected', 'parsed', 'completed', 'failed')),
    CONSTRAINT ck_email_ai_processing_status CHECK (ai_processing_status IN ('not_started', 'pending', 'completed', 'failed')),
    CONSTRAINT ck_email_record_status CHECK (record_status IN ('active', 'archived', 'deleted'))
);

CREATE INDEX ix_email_account_received_at ON emails (mailbox_account_id, received_at DESC);
CREATE INDEX ix_email_account_thread_id ON emails (mailbox_account_id, provider_thread_id);
CREATE INDEX ix_email_account_processing_status ON emails (mailbox_account_id, processing_status);
CREATE INDEX ix_email_account_record_status ON emails (mailbox_account_id, record_status);

CREATE TRIGGER trg_emails_updated_at
BEFORE UPDATE ON emails
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Table: attachments
CREATE TABLE attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id UUID NOT NULL,
    provider_attachment_id VARCHAR,
    provider_part_id VARCHAR,
    file_name TEXT,
    mime_type VARCHAR,
    size_bytes BIGINT,
    storage_bucket VARCHAR NOT NULL DEFAULT 'email-attachments',
    storage_path TEXT,
    download_status VARCHAR NOT NULL DEFAULT 'pending',
    upload_error TEXT,
    uploaded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_attachments_email_id FOREIGN KEY (email_id) REFERENCES emails (id) ON DELETE RESTRICT,
    CONSTRAINT ck_attachment_identity CHECK (provider_attachment_id IS NOT NULL OR provider_part_id IS NOT NULL),
    CONSTRAINT ck_attachment_size_bytes CHECK (size_bytes >= 0),
    CONSTRAINT ck_attachment_download_status CHECK (download_status IN ('pending', 'downloading', 'uploaded', 'failed'))
);

CREATE UNIQUE INDEX uq_att_id_notnull ON attachments (email_id, provider_attachment_id) WHERE provider_attachment_id IS NOT NULL;
CREATE UNIQUE INDEX uq_att_part_notnull ON attachments (email_id, provider_part_id) WHERE provider_part_id IS NOT NULL;
CREATE INDEX ix_attachment_email_id ON attachments (email_id);

CREATE TRIGGER trg_attachments_updated_at
BEFORE UPDATE ON attachments
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Table: sync_runs
CREATE TABLE sync_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mailbox_account_id UUID NOT NULL,
    sync_type VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    sync_duration_seconds INTEGER,
    emails_found INTEGER NOT NULL DEFAULT 0,
    emails_processed INTEGER NOT NULL DEFAULT 0,
    emails_inserted INTEGER NOT NULL DEFAULT 0,
    emails_failed INTEGER NOT NULL DEFAULT 0,
    duplicates_skipped INTEGER NOT NULL DEFAULT 0,
    attachments_found INTEGER NOT NULL DEFAULT 0,
    attachments_uploaded INTEGER NOT NULL DEFAULT 0,
    attachments_failed INTEGER NOT NULL DEFAULT 0,
    api_request_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    sync_cursor_before TEXT,
    sync_cursor_after TEXT,
    fallback_full_sync_used BOOLEAN NOT NULL DEFAULT FALSE,
    error_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_sync_runs_mailbox_account_id FOREIGN KEY (mailbox_account_id) REFERENCES mailbox_accounts (id) ON DELETE RESTRICT,
    CONSTRAINT ck_sync_run_type CHECK (sync_type IN ('full', 'incremental')),
    CONSTRAINT ck_sync_run_status CHECK (status IN ('pending', 'running', 'completed', 'partial_failure', 'failed')),
    CONSTRAINT ck_sync_run_duration CHECK (sync_duration_seconds >= 0),
    CONSTRAINT ck_sync_run_completed_at CHECK (completed_at IS NULL OR completed_at >= started_at),
    CONSTRAINT ck_sync_run_emails_found CHECK (emails_found >= 0),
    CONSTRAINT ck_sync_run_emails_processed CHECK (emails_processed >= 0),
    CONSTRAINT ck_sync_run_emails_inserted CHECK (emails_inserted >= 0),
    CONSTRAINT ck_sync_run_emails_failed CHECK (emails_failed >= 0),
    CONSTRAINT ck_sync_run_duplicates_skipped CHECK (duplicates_skipped >= 0),
    CONSTRAINT ck_sync_run_attachments_found CHECK (attachments_found >= 0),
    CONSTRAINT ck_sync_run_attachments_uploaded CHECK (attachments_uploaded >= 0),
    CONSTRAINT ck_sync_run_attachments_failed CHECK (attachments_failed >= 0),
    CONSTRAINT ck_sync_run_api_request_count CHECK (api_request_count >= 0),
    CONSTRAINT ck_sync_run_error_count CHECK (error_count >= 0)
);

CREATE INDEX ix_sync_run_mailbox_account_id ON sync_runs (mailbox_account_id);

-- Table: sync_logs
CREATE TABLE sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sync_run_id UUID NOT NULL,
    level VARCHAR NOT NULL,
    message TEXT NOT NULL,
    metadata_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_sync_logs_sync_run_id FOREIGN KEY (sync_run_id) REFERENCES sync_runs (id) ON DELETE RESTRICT,
    CONSTRAINT ck_sync_log_level CHECK (level IN ('info', 'warning', 'error', 'debug'))
);

CREATE INDEX ix_sync_log_sync_run_id ON sync_logs (sync_run_id);

-- Table: sync_errors
CREATE TABLE sync_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sync_run_id UUID NOT NULL,
    gmail_message_id VARCHAR,
    mailbox_account_id UUID,
    api_endpoint VARCHAR,
    provider_attachment_id VARCHAR,
    error_type VARCHAR NOT NULL,
    error_message TEXT NOT NULL,
    error_stack TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    is_retryable BOOLEAN NOT NULL DEFAULT FALSE,
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_sync_errors_sync_run_id FOREIGN KEY (sync_run_id) REFERENCES sync_runs (id) ON DELETE RESTRICT,
    CONSTRAINT fk_sync_errors_mailbox_account_id FOREIGN KEY (mailbox_account_id) REFERENCES mailbox_accounts (id) ON DELETE SET NULL,
    CONSTRAINT ck_sync_error_retry_count CHECK (retry_count >= 0)
);

CREATE INDEX ix_sync_error_sync_run_id ON sync_errors (sync_run_id);

-- =========================================================
-- Row Level Security
-- Backend-only Gmail data engine: no public client access
-- =========================================================

ALTER TABLE public.mailbox_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sync_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sync_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sync_errors ENABLE ROW LEVEL SECURITY;

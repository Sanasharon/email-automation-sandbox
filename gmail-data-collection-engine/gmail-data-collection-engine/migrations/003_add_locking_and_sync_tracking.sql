-- Migration 003: Add distributed locking columns to mailbox_accounts
-- These columns support atomic lock acquisition with TTL-based stale lock recovery.

ALTER TABLE mailbox_accounts
    ADD COLUMN IF NOT EXISTS sync_lock_token VARCHAR,
    ADD COLUMN IF NOT EXISTS sync_locked_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS sync_lock_expires_at TIMESTAMPTZ;

-- Migration 004: Add incremental sync tracking columns to sync_runs

ALTER TABLE sync_runs
    ADD COLUMN IF NOT EXISTS history_pages_processed INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS incremental_message_ids_found INTEGER NOT NULL DEFAULT 0;

-- Update sync_run_status constraint to include 'cancelled'
ALTER TABLE sync_runs DROP CONSTRAINT IF EXISTS ck_sync_run_status;
ALTER TABLE sync_runs ADD CONSTRAINT ck_sync_run_status
    CHECK (status IN ('pending', 'running', 'completed', 'partial_failure', 'failed', 'cancelled'));

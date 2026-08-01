-- migrations/006_add_ai_tasks_table.sql
-- Migration: add ai_tasks queue table for background AI work

BEGIN;

CREATE TABLE IF NOT EXISTS ai_tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email_id UUID NULL REFERENCES emails(id) ON DELETE CASCADE,
    task_type VARCHAR(50) NOT NULL, -- 'classification' | 'priority' | future types
    payload JSONB NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending | processing | completed | failed
    result JSONB NULL,
    error TEXT NULL,
    attempts INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 3,
    scheduled_at TIMESTAMPTZ NULL,
    started_at TIMESTAMPTZ NULL,
    completed_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_ai_tasks_status ON ai_tasks(status);
CREATE INDEX IF NOT EXISTS ix_ai_tasks_scheduled_at ON ai_tasks(scheduled_at);
CREATE INDEX IF NOT EXISTS ix_ai_tasks_email_id ON ai_tasks(email_id);

COMMIT;
-- migrations/009_add_ai_task_queue_table.sql
BEGIN;

CREATE TABLE IF NOT EXISTS ai_task_queue (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email_id UUID NULL REFERENCES emails(id) ON DELETE CASCADE,
    task_type VARCHAR(50) NOT NULL,
    payload JSONB NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
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

CREATE INDEX IF NOT EXISTS ix_ai_task_queue_status ON ai_task_queue(status);
CREATE INDEX IF NOT EXISTS ix_ai_task_queue_scheduled_at ON ai_task_queue(scheduled_at);
CREATE INDEX IF NOT EXISTS ix_ai_task_queue_email_id ON ai_task_queue(email_id);

COMMIT;
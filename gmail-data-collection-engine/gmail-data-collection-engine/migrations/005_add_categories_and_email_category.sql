-- migrations/004_add_categories_and_email_category.sql
-- Migration: add categories and email_categories tables

BEGIN;

CREATE TABLE IF NOT EXISTS categories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_by UUID NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    active BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS email_categories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email_id UUID NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    confidence DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    assigned_by UUID NULL,
    assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    corrected BOOLEAN NOT NULL DEFAULT false,
    UNIQUE (email_id, category_id)
);

CREATE INDEX IF NOT EXISTS ix_email_categories_email_id ON email_categories(email_id);
CREATE INDEX IF NOT EXISTS ix_email_categories_category_id ON email_categories(category_id);

COMMIT;
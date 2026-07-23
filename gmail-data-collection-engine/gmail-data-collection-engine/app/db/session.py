from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

# Configure module logger
logger = logging.getLogger(__name__)

# Create PostgreSQL engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Log runtime DB configuration
logger.info(f"Runtime DATABASE_URL from settings: {settings.database_url}")
logger.info(f"SQLAlchemy engine URL: {engine.url}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def ensure_full_schema():
    try:
        with engine.begin() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto";'))

            # 1. user_roles & users
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_roles (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(50) UNIQUE NOT NULL,
                    permissions_json JSONB NOT NULL DEFAULT '[]'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    role_id UUID NOT NULL REFERENCES user_roles(id) ON DELETE RESTRICT,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL DEFAULT 'User',
                    hashed_password VARCHAR(255) NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT true,
                    last_login TIMESTAMPTZ NULL,
                    is_deleted BOOLEAN NOT NULL DEFAULT false,
                    deleted_at TIMESTAMPTZ NULL,
                    deleted_by UUID NULL,
                    version INT NOT NULL DEFAULT 1,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """))

            # 2. mailbox_accounts columns
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS mailbox_accounts (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    provider VARCHAR NOT NULL DEFAULT 'gmail',
                    account_identifier VARCHAR NOT NULL,
                    auth_mode VARCHAR NOT NULL DEFAULT 'desktop_oauth',
                    last_history_id VARCHAR NULL,
                    last_sync_at TIMESTAMPTZ NULL,
                    sync_status VARCHAR NOT NULL DEFAULT 'connected',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """))
            conn.execute(text("ALTER TABLE mailbox_accounts ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE CASCADE;"))
            conn.execute(text("ALTER TABLE mailbox_accounts ADD COLUMN IF NOT EXISTS sync_lock_token VARCHAR NULL;"))
            conn.execute(text("ALTER TABLE mailbox_accounts ADD COLUMN IF NOT EXISTS sync_locked_at TIMESTAMPTZ NULL;"))
            conn.execute(text("ALTER TABLE mailbox_accounts ADD COLUMN IF NOT EXISTS sync_lock_expires_at TIMESTAMPTZ NULL;"))

            # 3. workflows & workflow_executions
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS workflows (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    mailbox_account_id UUID NOT NULL REFERENCES mailbox_accounts(id) ON DELETE CASCADE,
                    name VARCHAR(150) NOT NULL,
                    description VARCHAR NULL,
                    trigger_conditions_json JSONB NOT NULL,
                    actions_json JSONB NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT true,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS workflow_executions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
                    email_id UUID NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
                    status VARCHAR(20) NOT NULL,
                    execution_logs_json JSONB NOT NULL DEFAULT '[]'::jsonb,
                    executed_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """))

            # 4. templates & system_settings
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS templates (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NULL REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS system_settings (
                    key VARCHAR(100) PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
            """))

            # 5. indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_workflows_mailbox_id ON workflows(mailbox_account_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_workflow_executions_workflow_id ON workflow_executions(workflow_id);"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_workflow_executions_email_id ON workflow_executions(email_id);"))

            logger.info("Database full schema verification complete.")
    except Exception as e:
        logger.warning(f"Database schema auto-check notice: {e}")

# Automatically synchronize database schema on startup
ensure_full_schema()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

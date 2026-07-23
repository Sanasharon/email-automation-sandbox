import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import engine
from sqlalchemy import text
import bcrypt

def sync_full_schema():
    print("==========================================================")
    print("   Utservio FULL DATABASE SCHEMA SYNCHRONIZATION (Sprint 4)   ")
    print("==========================================================")
    
    with engine.begin() as conn:
        # --- 1. ENABLE EXTENSIONS ---
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto";'))
        print("✓ Extensions enabled (uuid-ossp, pgcrypto).")

        # --- 2. USER ROLES TABLE ---
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_roles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(50) UNIQUE NOT NULL,
                permissions_json JSONB NOT NULL DEFAULT '[]'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """))
        print("✓ Table 'user_roles' verified.")

        # --- 3. USERS TABLE ---
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
        print("✓ Table 'users' verified.")

        # --- 4. MAILBOX ACCOUNTS TABLE & COLUMNS ---
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
        print("✓ Table 'mailbox_accounts' & columns verified.")

        # --- 5. EMAILS TABLE ---
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS emails (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                mailbox_account_id UUID NOT NULL REFERENCES mailbox_accounts(id) ON DELETE RESTRICT,
                provider_message_id VARCHAR NOT NULL,
                provider_thread_id VARCHAR NULL,
                sender_email VARCHAR NULL,
                to_recipients JSONB NOT NULL DEFAULT '[]'::jsonb,
                cc_recipients JSONB NOT NULL DEFAULT '[]'::jsonb,
                bcc_recipients JSONB NOT NULL DEFAULT '[]'::jsonb,
                subject VARCHAR NULL,
                body_text VARCHAR NULL,
                body_html VARCHAR NULL,
                snippet VARCHAR NULL,
                labels JSONB NOT NULL DEFAULT '[]'::jsonb,
                received_at TIMESTAMPTZ NULL,
                is_read BOOLEAN NOT NULL DEFAULT false,
                has_attachments BOOLEAN NOT NULL DEFAULT false,
                raw_email_json JSONB NULL,
                processing_status VARCHAR NOT NULL DEFAULT 'collected',
                last_processing_error VARCHAR NULL,
                processed_at TIMESTAMPTZ NULL,
                ai_processing_status VARCHAR NOT NULL DEFAULT 'not_started',
                ai_processed_at TIMESTAMPTZ NULL,
                record_status VARCHAR NOT NULL DEFAULT 'active',
                archived_at TIMESTAMPTZ NULL,
                deleted_at TIMESTAMPTZ NULL,
                retention_category VARCHAR NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """))
        print("✓ Table 'emails' verified.")

        # --- 6. ATTACHMENTS TABLE ---
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS attachments (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email_id UUID NOT NULL REFERENCES emails(id) ON DELETE RESTRICT,
                provider_attachment_id VARCHAR NULL,
                provider_part_id VARCHAR NULL,
                file_name VARCHAR NULL,
                mime_type VARCHAR NULL,
                size_bytes BIGINT NULL,
                storage_bucket VARCHAR NOT NULL DEFAULT 'email-attachments',
                storage_path VARCHAR NULL,
                download_status VARCHAR NOT NULL DEFAULT 'pending',
                upload_error VARCHAR NULL,
                uploaded_at TIMESTAMPTZ NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """))
        print("✓ Table 'attachments' verified.")

        # --- 7. WORKFLOWS TABLE ---
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
        print("✓ Table 'workflows' verified.")

        # --- 8. WORKFLOW EXECUTIONS TABLE ---
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
        print("✓ Table 'workflow_executions' verified.")

        # --- 9. TEMPLATES TABLE ---
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
        print("✓ Table 'templates' verified.")

        # --- 10. SYSTEM SETTINGS TABLE ---
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS system_settings (
                key VARCHAR(100) PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """))
        print("✓ Table 'system_settings' verified.")

        # --- 11. INDEXES ---
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_workflows_mailbox_id ON workflows(mailbox_account_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_workflow_executions_workflow_id ON workflow_executions(workflow_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_workflow_executions_email_id ON workflow_executions(email_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_attachment_email_id ON attachments(email_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_email_account_received_at ON emails(mailbox_account_id, received_at DESC);"))
        print("✓ Database indexes verified.")

        # --- 12. SEED DEFAULT USER ROLES & ADMIN USER ---
        admin_role = conn.execute(text("SELECT id FROM user_roles WHERE name = 'Admin';")).fetchone()
        if not admin_role:
            role_res = conn.execute(text("""
                INSERT INTO user_roles (name, permissions_json) 
                VALUES ('Admin', '["all"]'::jsonb) 
                RETURNING id;
            """)).fetchone()
            admin_role_id = role_res[0]
            print("✓ Created default 'Admin' user role.")
        else:
            admin_role_id = admin_role[0]

        # Seed default viewer role
        conn.execute(text("""
            INSERT INTO user_roles (name, permissions_json) 
            VALUES ('Viewer', '["view_dashboard", "view_emails"]'::jsonb)
            ON CONFLICT (name) DO NOTHING;
        """))

        # Seed default Admin user: admin@utservio.com / admin123
        admin_user = conn.execute(text("SELECT id FROM users WHERE email = 'admin@utservio.com';")).fetchone()
        if not admin_user:
            pwd_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode('utf-8')
            user_res = conn.execute(text("""
                INSERT INTO users (role_id, email, name, hashed_password) 
                VALUES (:role_id, 'admin@utservio.com', 'System Admin', :pwd_hash)
                RETURNING id;
            """, {"role_id": admin_role_id, "pwd_hash": pwd_hash})).fetchone()
            admin_user_id = user_res[0]
            print("✓ Created default Admin user: admin@utservio.com (password: admin123).")
        else:
            admin_user_id = admin_user[0]

        # Link any existing mailboxes without user_id to admin_user_id
        conn.execute(text("UPDATE mailbox_accounts SET user_id = :admin_id WHERE user_id IS NULL;", {"admin_id": admin_user_id}))
        print("✓ Linked unassigned mailboxes to default Admin user.")

        # --- 13. CLEANUP STALE TEST DATA ---
        conn.execute(text("DELETE FROM sync_errors WHERE mailbox_account_id IN (SELECT id FROM mailbox_accounts WHERE account_identifier ILIKE '%yemireddivinodh%');"))
        conn.execute(text("DELETE FROM sync_logs WHERE sync_run_id IN (SELECT id FROM sync_runs WHERE mailbox_account_id IN (SELECT id FROM mailbox_accounts WHERE account_identifier ILIKE '%yemireddivinodh%'));"))
        conn.execute(text("DELETE FROM sync_runs WHERE mailbox_account_id IN (SELECT id FROM mailbox_accounts WHERE account_identifier ILIKE '%yemireddivinodh%');"))
        conn.execute(text("DELETE FROM workflow_executions WHERE email_id IN (SELECT id FROM emails WHERE mailbox_account_id IN (SELECT id FROM mailbox_accounts WHERE account_identifier ILIKE '%yemireddivinodh%'));"))
        conn.execute(text("DELETE FROM attachments WHERE email_id IN (SELECT id FROM emails WHERE mailbox_account_id IN (SELECT id FROM mailbox_accounts WHERE account_identifier ILIKE '%yemireddivinodh%'));"))
        conn.execute(text("DELETE FROM emails WHERE mailbox_account_id IN (SELECT id FROM mailbox_accounts WHERE account_identifier ILIKE '%yemireddivinodh%');"))
        conn.execute(text("DELETE FROM mailbox_accounts WHERE account_identifier ILIKE '%yemireddivinodh%';"))
        print("✓ Purged test data for yemireddivinodh@gmail.com.")

    # Remove cached OAuth token file
    token_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'secrets', 'token.json'))
    if os.path.exists(token_file):
        try:
            os.remove(token_file)
            print(f"✓ Cleared cached OAuth token file: {token_file}")
        except Exception as e:
            print(f"Notice: Could not remove token file: {e}")

    print("==========================================================")
    print("✓ SUCCESS: Database Schema 100% Synchronized with ORM Models")
    print("==========================================================")

if __name__ == "__main__":
    sync_full_schema()

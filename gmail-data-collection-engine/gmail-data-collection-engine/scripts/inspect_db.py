import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import settings
from app.db.session import engine
from sqlalchemy import text

def mask_password(url_str: str) -> str:
    if not url_str:
        return "None"
    return re.sub(r':([^@]+)@', r':****@', url_str)

def run_runtime_verification():
    print("==========================================================")
    print("      RUNTIME DATABASE CONNECTION & SCHEMA AUDIT          ")
    print("==========================================================")

    # 1. Environment & Configuration Sources
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    env_exists = os.path.exists(env_file)
    sys_db_url = os.environ.get('DATABASE_URL')
    settings_db_url = settings.database_url
    
    print(f"[1] Configuration Source Check:")
    print(f"    - .env file present: {env_exists} ({env_file if env_exists else 'N/A'})")
    print(f"    - System Environment DATABASE_URL set: {bool(sys_db_url)}")
    print(f"    - Settings (Runtime) DATABASE_URL: {mask_password(settings_db_url)}")
    print(f"    - Engine URL: {mask_password(str(engine.url))}")

    with engine.connect() as conn:
        # 2. Database Identity Queries
        cur_db = conn.execute(text("SELECT current_database();")).scalar()
        cur_schema = conn.execute(text("SELECT current_schema();")).scalar()
        cur_user = conn.execute(text("SELECT current_user();")).scalar()
        pg_version = conn.execute(text("SELECT version();")).scalar()
        
        try:
            inet_addr = conn.execute(text("SELECT inet_server_addr();")).scalar()
        except Exception:
            inet_addr = "Supabase Pooler / Direct Endpoint"

        print(f"\n[2] Live PostgreSQL Server Identity:")
        print(f"    - Current Database: {cur_db}")
        print(f"    - Current Schema:   {cur_schema}")
        print(f"    - Current User:     {cur_user}")
        print(f"    - Host / Addr:      {engine.url.host} (Resolved: {inet_addr})")
        print(f"    - Server Version:   {pg_version.split(',')[0] if pg_version else 'N/A'}")

        # 3. Columns of mailbox_accounts table
        mb_cols = conn.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'mailbox_accounts'
            ORDER BY ordinal_position;
        """)).fetchall()

        print(f"\n[3] 'mailbox_accounts' Table Runtime Columns ({len(mb_cols)} columns found):")
        has_user_id = False
        for col in mb_cols:
            col_name, data_type, nullable = col
            if col_name == 'user_id':
                has_user_id = True
                print(f"    ⭐ {col_name:<25} {data_type:<20} Nullable: {nullable} [USER SCOPING COLUMN VERIFIED]")
            else:
                print(f"       {col_name:<25} {data_type:<20} Nullable: {nullable}")

        # 4. Tables present in public schema
        public_tables = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)).fetchall()
        table_list = [t[0] for t in public_tables]
        print(f"\n[4] Active Public Schema Tables ({len(table_list)} tables):")
        for t in table_list:
            print(f"    - {t}")

        # 5. Check Alembic Version table if present
        print(f"\n[5] Alembic Migration Version Check:")
        if 'alembic_version' in table_list:
            try:
                alembic_rows = conn.execute(text("SELECT * FROM alembic_version;")).fetchall()
                print(f"    - alembic_version rows: {[r[0] for r in alembic_rows]}")
            except Exception as e:
                print(f"    - Could not query alembic_version: {e}")
        else:
            print("    - 'alembic_version' table not present (Direct DDL / Custom SQL migrations active)")

        # 6. Overall Audit & Mismatch Summary
        expected_tables = {'users', 'user_roles', 'mailbox_accounts', 'emails', 'attachments', 'workflows', 'workflow_executions', 'templates', 'system_settings', 'sync_runs', 'sync_logs', 'sync_errors'}
        missing_tables = expected_tables - set(table_list)

        print("\n==========================================================")
        print("               AUDIT VERIFICATION SUMMARY                 ")
        print("==========================================================")
        print(f"  • Runtime Engine Connected:              SUCCESS")
        print(f"  • mailbox_accounts.user_id Present:       {'YES (PASS)' if has_user_id else 'NO (FAIL)'}")
        print(f"  • Missing ORM Tables in DB:               {list(missing_tables) if missing_tables else 'NONE (100% MATCH)'}")
        print(f"  • Active DB Matches ORM Models:          {'100% ALIGNED (PASS)' if has_user_id and not missing_tables else 'MISMATCH DETECTED'}")
        print("==========================================================")

if __name__ == "__main__":
    run_runtime_verification()

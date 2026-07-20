import os
import re
from sqlalchemy import create_engine, text

# Load .env file manually (simple parser)
def load_env(path):
    env = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, val = line.split('=', 1)
            env[key] = val
    return env

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
env = load_env(env_path)

DATABASE_URL = env.get('DATABASE_URL')
print('DATABASE_URL:', DATABASE_URL)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
with engine.connect() as conn:
    # Current database
    cur_db = conn.execute(text('SELECT current_database()')).scalar()
    print('Current database:', cur_db)

    # Check if users table exists
    tables = conn.execute(text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name='users';
    """)).fetchall()
    print('Users table exists:', bool(tables))

    # List columns if table exists
    if tables:
        cols = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name='users'
            ORDER BY ordinal_position;
        """)).fetchall()
        print('Columns in users table:')
        for col in cols:
            print(' -', col[0])

    # Alembic version table
    versions = conn.execute(text("SELECT * FROM alembic_version"))
    rows = versions.fetchall()
    print('Alembic version rows:')
    for row in rows:
        print(row)

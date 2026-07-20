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

def get_db():
    db = SessionLocal()
    try:
        # Log current DB, schema, and search_path
        cur_db = db.execute(text("SELECT current_database()")).scalar()
        logger.info(f"Current database: {cur_db}")
        cur_schema = db.execute(text("SELECT current_schema()")).scalar()
        logger.info(f"Current schema: {cur_schema}")
        search_path = db.execute(text("SHOW search_path")).scalar()
        logger.info(f"Search path: {search_path}")

        # Log columns of users table
        cols = db.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='users' ORDER BY ordinal_position"
        )).fetchall()
        column_names = [c[0] for c in cols]
        logger.info(f"Columns in users table (runtime): {column_names}")
        yield db
    finally:
        db.close()

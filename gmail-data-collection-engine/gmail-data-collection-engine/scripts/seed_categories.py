# scripts/seed_categories.py
"""
Seed default categories:
- Sales
- Support
- Billing
- HR
- General

Usage:
python scripts/seed_categories.py
"""
import os
from sqlalchemy import create_engine, text
from app.config import settings

DEFAULT_CATEGORIES = [
    {"name": "Sales", "description": "Sales related enquiries"},
    {"name": "Support", "description": "Customer support and tickets"},
    {"name": "Billing", "description": "Invoices, payments and billing"},
    {"name": "HR", "description": "Human Resources and hiring"},
    {"name": "General", "description": "General communications"},
]

def main():
    db_url = settings.database_url
    engine = create_engine(db_url)
    with engine.begin() as conn:
        for c in DEFAULT_CATEGORIES:
            # upsert: insert if not exists
            conn.execute(text("""
            INSERT INTO categories (name, description, created_at, updated_at, active)
            VALUES (:name, :description, now(), now(), true)
            ON CONFLICT (name) DO UPDATE SET description = EXCLUDED.description, updated_at = now();
            """), c)
    print("Seeded default categories.")

if __name__ == "__main__":
    main()
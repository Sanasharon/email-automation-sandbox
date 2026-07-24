"""
Script to update admin user password.
"""
import os
import sys
from pathlib import Path

# Navigate to the parent directory where the app module is located
script_dir = Path(__file__).parent
app_dir = script_dir.parent
sys.path.insert(0, str(app_dir))

import bcrypt
from app.db.session import SessionLocal
from app.models.user import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_password():
    """Update admin user password."""
    db = SessionLocal()
    try:
        email = "testauth@example.com"
        new_password = "password"
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.error(f"User {email} not found")
            return False
        
        # Hash the new password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
        
        user.hashed_password = hashed_password
        db.commit()
        
        logger.info(f"✓ Password updated for {email}")
        logger.info(f"  New password: {new_password}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update password: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    update_password()

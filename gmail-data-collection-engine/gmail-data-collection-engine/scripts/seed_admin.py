import sys
import os
import bcrypt
from datetime import datetime

# Add the project root to the path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.models.user import User, UserRole

def seed_admin():
    db = SessionLocal()
    try:
        # Create an Admin role if it doesn't exist
        admin_role = db.query(UserRole).filter(UserRole.name == "Admin").first()
        if not admin_role:
            admin_role = UserRole(
                name="Admin",
                permissions_json=["*"]  # Gives all permissions
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("Admin role created.")

        # Create the test user if it doesn't exist
        email = "testauth@example.com"
        password = "password123"
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Hash the password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            new_user = User(
                email=email,
                name="Admin User",
                hashed_password=hashed_password,
                role_id=admin_role.id,
                is_active=True
            )
            db.add(new_user)
            db.commit()
            print(f"User {email} created successfully with password '{password}'.")
        else:
            print(f"User {email} already exists.")
            
    except Exception as e:
        print(f"Error seeding admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()

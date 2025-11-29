# Health and Fitness Club Management System
# Afaq Virk 101338854
# Raymond Liu 101264487

import sys
from pathlib import Path

# Add parent directory to path so we can import models
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from models import User, Role
from app.member import member_menu
from app.trainer import trainer_menu
from app.admin import admin_menu
from app.cli_utils import init_console, menu, header, pause, clear_screen, sleep, error
from app.auth import ensure_database_exists, build_database_url
from app.seed import reset_and_seed

# Database Configuration (supports DATABASE_URL or PG* variables)
ensure_database_exists()
DATABASE_URL = build_database_url()
if not DATABASE_URL:
    raise RuntimeError(
        "Database configuration not found. Provide "
        "PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD in your environment/.env."
    )


def get_db_session():
    """Create and return a database session"""
    engine = create_engine(DATABASE_URL, echo=False)
    SessionFactory = sessionmaker(bind=engine)
    return SessionFactory()


def login(session):
    """Authenticate user and return user object"""
    header("Login")
    
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    # SELECT * FROM user WHERE email = ? AND password = ? LIMIT 1
    user = session.query(User).filter_by(email=email, password=password).first()
    
    if user:
        print(f"\nWelcome, {user.first_name} {user.last_name}!")
        sleep(1.0)
        return user
    else:
        error("Invalid credentials. Please try again.")
        sleep(1.2)
        return None


def register_member(session):
    """Register a new member"""
    header("Member Registration")
    
    try:
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        
        dob_str = input("Date of Birth (YYYY-MM-DD): ").strip()
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        
        sex = input("Sex (M/F/O): ").strip().upper()
        phone = input("Phone: ").strip()
        
        # Get Member role
        # SELECT * FROM role WHERE name = 'Member' LIMIT 1
        member_role = session.query(Role).filter_by(name='Member').first()
        
        new_user = User(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=dob,
            sex=sex,
            phone=phone,
            role=member_role.id
        )
        
        session.add(new_user)
        session.commit()
        print("\n[SUCCESS] Registration successful! You can now login.")
        pause()
    except Exception as e:
        session.rollback()
        error(f"Registration failed: {e}")
        pause()


def main():
    """Main application entry point"""
    # Support reset flag for test setup used for our video demo
    if any(arg in ("--reset", "-r") for arg in sys.argv[1:]):
        print("Resetting and seeding the database...")
        reset_and_seed(DATABASE_URL)
        print("[SUCCESS] Database reset and seed complete.")
        return

    init_console()
    clear_screen()
    header("Health and Fitness Club Management System")
    sleep(1)
    
    # Create database session
    db_session = get_db_session()
    
    try:
        while True:
            choice = menu("Main Menu", ["Login", "Register (Member)", "Exit"])
            
            if choice == '1':
                user = login(db_session)
                if user:
                    role_name = user.role_obj.name
                    
                    if role_name == 'Member':
                        member_menu(db_session, user)
                    elif role_name == 'Trainer':
                        trainer_menu(db_session, user)
                    elif role_name == 'Admin':
                        admin_menu(db_session, user)
            
            elif choice == '2':
                register_member(db_session)
            
            elif choice == '3':
                clear_screen()
                header("Goodbye")
                print("Thank you for using the Health and Fitness Club Management System!")
                break
            
            else:
                error("Invalid choice!")
                pause()
    
    finally:
        db_session.close()


if __name__ == "__main__":
    main()


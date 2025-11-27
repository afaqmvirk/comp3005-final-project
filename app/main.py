# Health and Fitness Club Management System
# Afak
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

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@address/Final_Project")


def get_db_session():
    """Create and return a database session"""
    engine = create_engine(DATABASE_URL, echo=False)
    SessionFactory = sessionmaker(bind=engine)
    return SessionFactory()


def login(session):
    """Authenticate user and return user object"""
    print("\n LOGIN \n")
    
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    # SELECT * FROM user WHERE email = ? AND password = ? LIMIT 1
    user = session.query(User).filter_by(email=email, password=password).first()
    
    if user:
        print(f"\nWelcome, {user.first_name} {user.last_name}!")
        return user
    else:
        print("\nInvalid credentials. Please try again.")
        return None


def register_member(session):
    """Register a new member"""
    print("\n MEMBER REGISTRATION \n")
    
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
    except Exception as e:
        session.rollback()
        print(f"\n[ERROR] Registration failed: {e}")


def main():
    """Main application entry point"""
    print("\n HEALTH AND FITNESS CLUB MANAGEMENT SYSTEM\n")
    
    # Create database session
    db_session = get_db_session()
    
    try:
        while True:
            print("\n1. Login")
            print("2. Register (Member)")
            print("3. Exit")
            
            choice = input("\nChoice: ").strip()
            
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
                print("\nThank you for using the Health and Fitness Club Management System!")
                break
            
            else:
                print("\n[ERROR] Invalid choice!")
    
    finally:
        db_session.close()


if __name__ == "__main__":
    main()


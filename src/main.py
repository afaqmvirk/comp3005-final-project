# Health and Fitness Club Management System
# Afak
# Raymond Liu 101264487

from sqlalchemy import create_engine, Column, Integer, String, Date, Time, Boolean, DECIMAL, CHAR, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
from decimal import Decimal
import os

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@address/Final_Project")
Base = declarative_base()

class Role(Base):
    """Role lookup table - Member, Trainer, Admin"""
    __tablename__ = 'role'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    
    users = relationship("User", back_populates="role_obj")


class User(Base):
    """User entity - represents Members, Trainers, and Admins"""
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date)
    sex = Column(CHAR(1), CheckConstraint("sex IN ('M', 'F', 'O')"))
    phone = Column(String(20))
    role = Column(Integer, ForeignKey('role.id'), nullable=False)
    
    role_obj = relationship("Role", back_populates="users")
    metrics = relationship("Metric", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="trainer", foreign_keys="Schedule.trainer_id")
    enrollments = relationship("Enrollment", back_populates="member")
    bills_as_member = relationship("Bill", back_populates="member", foreign_keys="Bill.member_id")
    bills_as_admin = relationship("Bill", back_populates="admin", foreign_keys="Bill.admin_id")


class Service(Base):
    """Service offerings and pricing"""
    __tablename__ = 'service'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    
    items = relationship("Item", back_populates="service")


class Bill(Base):
    """Billing records"""
    __tablename__ = 'bill'
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    member_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    date = Column(Date, nullable=False)
    paid = Column(Boolean, default=False)
    
    admin = relationship("User", back_populates="bills_as_admin", foreign_keys=[admin_id])
    member = relationship("User", back_populates="bills_as_member", foreign_keys=[member_id])
    items = relationship("Item", back_populates="bill", cascade="all, delete-orphan")


class Item(Base):
    """Line items on bills"""
    __tablename__ = 'item'
    
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey('bill.id', ondelete='CASCADE'), nullable=False)
    service_id = Column(Integer, ForeignKey('service.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    
    bill = relationship("Bill", back_populates="items")
    service = relationship("Service", back_populates="items")


class MetricType(Base):
    """Types of health metrics"""
    __tablename__ = 'metric_type'
    
    id = Column(Integer, primary_key=True)
    metric_name = Column(String(100), nullable=False)
    metric_desc = Column(Text)
    
    metrics = relationship("Metric", back_populates="metric_type_obj")


class Metric(Base):
    """Health metrics logged by members"""
    __tablename__ = 'metric'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    metric_type = Column(Integer, ForeignKey('metric_type.id'), nullable=False)
    value = Column(DECIMAL(10, 2), nullable=False)
    logged_date = Column(DateTime, nullable=False, default=datetime.now)
    
    user = relationship("User", back_populates="metrics")
    metric_type_obj = relationship("MetricType", back_populates="metrics")
    goals = relationship("Goal", back_populates="target_metric")


class Goal(Base):
    """Fitness goals set by members"""
    __tablename__ = 'goal'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    metric_id = Column(Integer, ForeignKey('metric.id'), nullable=False)
    goal_date = Column(Date, nullable=False)
    
    user = relationship("User", back_populates="goals")
    target_metric = relationship("Metric", back_populates="goals")


class Room(Base):
    """Physical rooms/spaces in the facility"""
    __tablename__ = 'room'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    capacity = Column(Integer, nullable=False)
    
    equipment = relationship("Equipment", back_populates="room")


class EquipmentStatus(Base):
    """Equipment status lookup table"""
    __tablename__ = 'equipment_status'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False, unique=True)
    
    equipment = relationship("Equipment", back_populates="status")


class Equipment(Base):
    """Gym equipment"""
    __tablename__ = 'equipment'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'))
    status_id = Column(Integer, ForeignKey('equipment_status.id'), nullable=False)
    
    room = relationship("Room", back_populates="equipment")
    status = relationship("EquipmentStatus", back_populates="equipment")


class ScheduleType(Base):
    """Schedule type lookup - Group Class, Personal Training, Consultation"""
    __tablename__ = 'schedule_type'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False, unique=True)
    
    schedules = relationship("Schedule", back_populates="schedule_type_obj")


class Schedule(Base):
    """Trainer availability and session schedules"""
    __tablename__ = 'schedule'
    
    id = Column(Integer, primary_key=True)
    trainer_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    type = Column(Integer, ForeignKey('schedule_type.id'), nullable=False)
    
    trainer = relationship("User", back_populates="schedules", foreign_keys=[trainer_id])
    schedule_type_obj = relationship("ScheduleType", back_populates="schedules")
    session = relationship("Session", back_populates="schedule", uselist=False, cascade="all, delete-orphan")


class Session(Base):
    """Training sessions and group classes"""
    __tablename__ = 'session'
    
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('schedule.id', ondelete='CASCADE'), nullable=False)
    size = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    desc = Column(Text)
    location = Column(String(255))
    sex_restrict = Column(CHAR(1), CheckConstraint("sex_restrict IN ('M', 'F', 'A')"))
    
    schedule = relationship("Schedule", back_populates="session")
    enrollments = relationship("Enrollment", back_populates="session", cascade="all, delete-orphan")


class Enrollment(Base):
    """Member enrollment in sessions"""
    __tablename__ = 'enrollment'
    __table_args__ = (UniqueConstraint('session_id', 'member_id'),)
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('session.id', ondelete='CASCADE'), nullable=False)
    member_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    attended = Column(Boolean, default=False)
    
    session = relationship("Session", back_populates="enrollments")
    member = relationship("User", back_populates="enrollments")


# Database connect

def get_db_session():
    """Create and return a database session"""
    engine = create_engine(DATABASE_URL, echo=False)
    SessionFactory = sessionmaker(bind=engine)
    return SessionFactory()


# Authentication

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


# Member stuff

def member_dashboard(session, user):
    """Display member's personalized dashboard"""
    print("\n MEMBER DASHBOARD \n")
    
    # Recent health metrics
    # SELECT * FROM metric WHERE user_id = ? ORDER BY logged_date DESC LIMIT 5
    recent_metrics = session.query(Metric).filter_by(user_id=user.id)\
        .order_by(Metric.logged_date.desc()).limit(5).all()
    
    if recent_metrics:
        print("\nRecent Health Metrics:")
        for metric in recent_metrics:
            print(f"  - {metric.metric_type_obj.metric_name}: {metric.value} "
                  f"({metric.logged_date.strftime('%Y-%m-%d %H:%M')})")
    else:
        print("\nNo health metrics recorded yet.")
    
    # Active goals
    # SELECT * FROM goal WHERE user_id = ?
    goals = session.query(Goal).filter_by(user_id=user.id).all()
    if goals:
        print(f"\nActive Fitness Goals: {len(goals)}")
        for goal in goals:
            metric = goal.target_metric
            print(f"  - Target: {metric.metric_type_obj.metric_name} = {metric.value} by {goal.goal_date}")
    else:
        print("\nNo fitness goals set yet.")
    
    # Upcoming enrollments
    today = date.today()
    # SELECT * FROM enrollment JOIN session ON enrollment.session_id = session.id JOIN schedule ON session.schedule_id = schedule.id WHERE enrollment.member_id = ? AND schedule.date >= ? ORDER BY schedule.date, schedule.start_time LIMIT 5
    upcoming = session.query(Enrollment).join(Session).join(Schedule)\
        .filter(Enrollment.member_id == user.id, Schedule.date >= today)\
        .order_by(Schedule.date, Schedule.start_time).limit(5).all()
    
    if upcoming:
        print("\nUpcoming Sessions:")
        for enrollment in upcoming:
            sched = enrollment.session.schedule
            print(f"  - {enrollment.session.name} - {sched.date} at {sched.start_time}")
    else:
        print("\nNo upcoming sessions scheduled.")


def manage_profile(session, user):
    """Update member profile information"""
    print("\n MANAGE PROFILE \n")
    
    print("\nCurrent Information:")
    print(f"Name: {user.first_name} {user.last_name}")
    print(f"Email: {user.email}")
    print(f"Phone: {user.phone or 'Not set'}")
    print(f"Date of Birth: {user.date_of_birth or 'Not set'}")
    print(f"Sex: {user.sex or 'Not set'}")
    
    print("\nWhat would you like to update?")
    print("1. Phone Number")
    print("2. Password")
    print("3. Back")
    
    choice = input("\nChoice: ").strip()
    
    if choice == '1':
        new_phone = input("New phone number: ").strip()
        user.phone = new_phone
        session.commit()
        print("[SUCCESS] Phone number updated successfully!")
    elif choice == '2':
        new_password = input("New password: ").strip()
        confirm = input("Confirm password: ").strip()
        if new_password == confirm:
            user.password = new_password
            session.commit()
            print("[SUCCESS] Password updated successfully!")
        else:
            print("[ERROR] Passwords don't match!")


def log_health_metrics(session, user):
    """Log new health metrics"""
    print("\n LOG HEALTH METRICS \n")
    
    # Display available metric types
    # SELECT * FROM metric_type
    metric_types = session.query(MetricType).all()
    print("\nAvailable Metrics:")
    for mt in metric_types:
        print(f"{mt.id}. {mt.metric_name} - {mt.metric_desc}")
    
    try:
        metric_type_id = int(input("\nSelect metric type (number): ").strip())
        value = float(input("Enter value: ").strip())
        
        new_metric = Metric(
            user_id=user.id,
            metric_type=metric_type_id,
            value=Decimal(str(value)),
            logged_date=datetime.now()
        )
        
        session.add(new_metric)
        session.commit()
        print("[SUCCESS] Health metric logged successfully!")
    except ValueError:
        print("[ERROR] Invalid input!")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Error: {e}")


def view_health_metrics(session, user):
    """View health metrics history with trend analysis"""
    print("\n HEALTH METRICS HISTORY \n")
    
    # Get all metrics grouped by type
    # SELECT * FROM metric_type
    metric_types = session.query(MetricType).all()
    
    for mt in metric_types:
        # SELECT * FROM metric WHERE user_id = ? AND metric_type = ? ORDER BY logged_date
        metrics = session.query(Metric).filter_by(
            user_id=user.id, 
            metric_type=mt.id
        ).order_by(Metric.logged_date).all()
        
        if metrics:
            print(f"\n{mt.metric_name}:")
            for metric in metrics:
                print(f"  - {metric.logged_date.strftime('%Y-%m-%d')}: {metric.value}")
            
            # Simple trend analysis
            if len(metrics) >= 2:
                first_val = float(metrics[0].value)
                last_val = float(metrics[-1].value)
                change = last_val - first_val
                if change > 0:
                    print(f"  Trend: +{change:.2f} (increased)")
                elif change < 0:
                    print(f"  Trend: {change:.2f} (decreased)")
                else:
                    print("  Trend: No change")


def set_fitness_goals(session, user):
    """Set new fitness goals"""
    print("\n SET FITNESS GOALS \n")
    
    # Display available metrics
    # SELECT * FROM metric_type
    metric_types = session.query(MetricType).all()
    print("\nSelect metric type for your goal:")
    for mt in metric_types:
        print(f"{mt.id}. {mt.metric_name}")
    
    try:
        metric_type_id = int(input("\nMetric type: ").strip())
        target_value = float(input("Target value: ").strip())
        goal_date_str = input("Target date (YYYY-MM-DD): ").strip()
        goal_date = datetime.strptime(goal_date_str, '%Y-%m-%d').date()
        
        # Create a metric entry for the goal
        goal_metric = Metric(
            user_id=user.id,
            metric_type=metric_type_id,
            value=Decimal(str(target_value)),
            logged_date=datetime.now()
        )
        session.add(goal_metric)
        session.flush()
        
        # Create the goal
        new_goal = Goal(
            user_id=user.id,
            metric_id=goal_metric.id,
            goal_date=goal_date
        )
        session.add(new_goal)
        session.commit()
        print("[SUCCESS] Fitness goal set successfully!")
    except ValueError:
        print("[ERROR] Invalid input format!")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Error: {e}")


def cancel_session(session, user):
    """Cancel a scheduled session"""
    print("\n CANCEL SESSION \n")
    
    # Get user's upcoming enrollments
    today = date.today()
    # SELECT * FROM enrollment JOIN session ON enrollment.session_id = session.id JOIN schedule ON session.schedule_id = schedule.id WHERE enrollment.member_id = ? AND schedule.date >= ? ORDER BY schedule.date, schedule.start_time
    enrollments = session.query(Enrollment).join(Session).join(Schedule).filter(
        Enrollment.member_id == user.id,
        Schedule.date >= today
    ).order_by(Schedule.date, Schedule.start_time).all()
    
    if not enrollments:
        print("\nYou have no upcoming sessions to cancel.")
        return
    
    print("\nYour Upcoming Sessions:")
    for i, enrollment in enumerate(enrollments, 1):
        sess = enrollment.session
        sched = sess.schedule
        print(f"{i}. {sess.name} - {sched.date} at {sched.start_time}")
    
    try:
        choice = int(input("\nSelect session to cancel (0 to go back): ").strip())
        if choice == 0:
            return
        if 1 <= choice <= len(enrollments):
            selected = enrollments[choice - 1]
            session.delete(selected)
            session.commit()
            print("[SUCCESS] Session cancelled successfully!")
        else:
            print("[ERROR] Invalid selection!")
    except ValueError:
        print("[ERROR] Invalid input!")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Error: {e}")


def member_menu(session, user):
    """Member main menu"""
    while True:
        print("\n MEMBER MENU \n")
        print("1. View Dashboard")
        print("2. Manage Profile")
        print("3. Log Health Metrics")
        print("4. View Health Metrics History")
        print("5. Logout")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            member_dashboard(session, user)
        elif choice == '2':
            manage_profile(session, user)
        elif choice == '3':
            log_health_metrics(session, user)
        elif choice == '4':
            view_health_metrics(session, user)
        elif choice == '5':
            print("\nLogging out...")
            break
        else:
            print("[ERROR] Invalid choice!")
        
        input("\nPress Enter to continue...")


# Trainer stuff

def view_trainer_schedule(session, user):
    """View trainer's schedule and upcoming sessions"""
    print("\n MY SCHEDULE \n")
    
    today = date.today()
    # SELECT * FROM schedule WHERE trainer_id = ? AND date >= ? ORDER BY date, start_time
    schedules = session.query(Schedule).filter(
        Schedule.trainer_id == user.id,
        Schedule.date >= today
    ).order_by(Schedule.date, Schedule.start_time).all()
    
    if not schedules:
        print("\nNo upcoming schedule entries.")
        return
    
    print("\nUpcoming Schedule:")
    for sched in schedules:
        print(f"\n{sched.date} - {sched.start_time} to {sched.end_time}")
        print(f"Type: {sched.schedule_type_obj.type}")
        
        if sched.session:
            sess = sched.session
            print(f"Session: {sess.name}")
            # SELECT * FROM enrollment WHERE session_id = ?
            enrollments = session.query(Enrollment).filter_by(session_id=sess.id).all()
            print(f"Enrolled: {len(enrollments)}/{sess.size}")
            if enrollments:
                print("Participants:")
                for enrollment in enrollments:
                    member = enrollment.member
                    attended_status = "[X]" if enrollment.attended else "[ ]"
                    print(f"  {attended_status} {member.first_name} {member.last_name}")
        else:
            print("Status: Available (not booked)")


def set_availability(session, user):
    """Set trainer availability"""
    print("\n SET AVAILABILITY \n")
    
    print("\nSchedule Types:")
    # SELECT * FROM schedule_type
    schedule_types = session.query(ScheduleType).all()
    for st in schedule_types:
        print(f"{st.id}. {st.type}")
    
    try:
        date_str = input("\nDate (YYYY-MM-DD): ").strip()
        schedule_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        start_str = input("Start time (HH:MM): ").strip()
        start_time = datetime.strptime(start_str, '%H:%M').time()
        
        end_str = input("End time (HH:MM): ").strip()
        end_time = datetime.strptime(end_str, '%H:%M').time()
        
        sched_type = int(input("Schedule type: ").strip())
        
        # Check for overlapping schedules
        # SELECT * FROM schedule WHERE trainer_id = ? AND date = ? AND start_time < ? AND end_time > ? LIMIT 1
        overlapping = session.query(Schedule).filter(
            Schedule.trainer_id == user.id,
            Schedule.date == schedule_date,
            Schedule.start_time < end_time,
            Schedule.end_time > start_time
        ).first()
        
        if overlapping:
            print("[ERROR] This time slot overlaps with an existing schedule!")
            return
        
        new_schedule = Schedule(
            trainer_id=user.id,
            date=schedule_date,
            start_time=start_time,
            end_time=end_time,
            type=sched_type
        )
        session.add(new_schedule)
        session.commit()
        print("[SUCCESS] Availability added successfully!")
    except ValueError:
        print("[ERROR] Invalid input format!")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Error: {e}")


def view_member_profiles(session, user):
    """Search and view profiles of members assigned to this trainer"""
    print("\n MEMBER LOOKUP \n")
    
    # Get all members who have sessions with this trainer
    # SELECT DISTINCT user.* FROM user JOIN enrollment ON user.id = enrollment.member_id JOIN session ON enrollment.session_id = session.id JOIN schedule ON session.schedule_id = schedule.id WHERE schedule.trainer_id = ?
    members = session.query(User).join(Enrollment).join(Session).join(Schedule).filter(
        Schedule.trainer_id == user.id
    ).distinct().all()
    
    if not members:
        print("\nNo assigned members yet.")
        return
    
    # Search functionality
    search_name = input("\nSearch member by name (or press Enter to view all): ").strip()

    if search_name:
        filtered_members = [m for m in members if 
                           search_name.lower() in m.first_name.lower() or 
                           search_name.lower() in m.last_name.lower()]
        
        if not filtered_members:
            print(f"\nNo members found matching '{search_name}'")
            return
        
        members = filtered_members
    
    print(f"\nFound {len(members)} member(s):")
    for i, member in enumerate(members, 1):
        print(f"\n{i}. {member.first_name} {member.last_name}")
        print(f"   Email: {member.email}")
        print(f"   Phone: {member.phone or 'N/A'}")
        
        # Last (most recent) metric
        # SELECT * FROM metric WHERE user_id = ? ORDER BY logged_date DESC LIMIT 1
        last_metric = session.query(Metric).filter_by(user_id=member.id)\
            .order_by(Metric.logged_date.desc()).first()
        
        if last_metric:
            print(f"   Last Metric: {last_metric.metric_type_obj.metric_name} = {last_metric.value} "
                  f"({last_metric.logged_date.strftime('%Y-%m-%d')})")
        else:
            print("   Last Metric: None recorded")
        
        # Current goal
        # SELECT * FROM goal WHERE user_id = ? LIMIT 1
        goal = session.query(Goal).filter_by(user_id=member.id).first()
        if goal:
            target = goal.target_metric
            print(f"   Current Goal: {target.metric_type_obj.metric_name} = {target.value} by {goal.goal_date}")
        else:
            print("   Current Goal: None set")


def trainer_menu(session, user):
    """Trainer main menu"""
    while True:
        print("TRAINER MENU")
        print("1. View My Schedule")
        print("2. Set Availability")
        print("3. Member Lookup")
        print("4. Logout")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            view_trainer_schedule(session, user)
        elif choice == '2':
            set_availability(session, user)
        elif choice == '3':
            view_member_profiles(session, user)
        elif choice == '4':
            print("\nLogging out...")
            break
        else:
            print("[ERROR] Invalid choice!")
        
        input("\nPress Enter to continue...")


# Admin stuff

def manage_equipment(session, user):
    """Manage equipment maintenance and status"""
    print("\n EQUIPMENT MANAGEMENT \n")
    
    print("\n1. View All Equipment")
    print("2. Update Equipment Status")
    print("3. Back")
    
    choice = input("\nChoice: ").strip()
    
    if choice == '1':
        # SELECT * FROM equipment
        equipment_list = session.query(Equipment).all()
        print("\nEquipment List:")
        for eq in equipment_list:
            room_name = eq.room.name if eq.room else "N/A"
            print(f"{eq.id}. {eq.name} - Room: {room_name} - Status: {eq.status.type}")
    
    elif choice == '2':
        eq_id = int(input("\nEquipment ID: ").strip())
        # SELECT * FROM equipment WHERE id = ? LIMIT 1
        equipment = session.query(Equipment).filter_by(id=eq_id).first()
        
        if not equipment:
            print("[ERROR] Equipment not found!")
            return
        
        print(f"\nEquipment: {equipment.name}")
        print(f"Current Status: {equipment.status.type}")
        
        # SELECT * FROM equipment_status
        statuses = session.query(EquipmentStatus).all()
        print("\nAvailable Statuses:")
        for status in statuses:
            print(f"{status.id}. {status.type}")
        
        new_status = int(input("\nNew status ID: ").strip())
        equipment.status_id = new_status
        session.commit()
        print("[SUCCESS] Equipment status updated!")


def manage_class_schedule(session, user):
    """Create and manage group fitness classes"""
    print("\n CLASS SCHEDULE MANAGEMENT \n")
    
    print("\n1. View All Classes")
    print("2. Create New Class")
    print("3. Cancel Class")
    print("4. Back")
    
    choice = input("\nChoice: ").strip()
    
    if choice == '1':
        today = date.today()
        # SELECT * FROM session JOIN schedule ON session.schedule_id = schedule.id WHERE schedule.date >= ? ORDER BY schedule.date, schedule.start_time
        classes = session.query(Session).join(Schedule).filter(
            Schedule.date >= today
        ).order_by(Schedule.date, Schedule.start_time).all()
        
        print("\nUpcoming Classes:")
        for sess in classes:
            sched = sess.schedule
            # SELECT COUNT(*) FROM enrollment WHERE session_id = ?
            enrolled = session.query(Enrollment).filter_by(session_id=sess.id).count()
            print(f"{sess.id}. {sess.name} - {sched.date} at {sched.start_time}")
            print(f"   Trainer: {sched.trainer.first_name} {sched.trainer.last_name}")
            print(f"   Enrolled: {enrolled}/{sess.size}")
    
    elif choice == '2':
        try:
            # Get trainers
            # SELECT * FROM role WHERE name = 'Trainer' LIMIT 1
            trainer_role = session.query(Role).filter_by(name='Trainer').first()
            # SELECT * FROM user WHERE role = ?
            trainers = session.query(User).filter_by(role=trainer_role.id).all()
            
            print("\nTrainers:")
            for i, trainer in enumerate(trainers, 1):
                print(f"{i}. {trainer.first_name} {trainer.last_name}")
            
            trainer_choice = int(input("\nSelect trainer: ").strip())
            selected_trainer = trainers[trainer_choice - 1]
            
            # Get class details
            date_str = input("Date (YYYY-MM-DD): ").strip()
            class_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            start_str = input("Start time (HH:MM): ").strip()
            start_time = datetime.strptime(start_str, '%H:%M').time()
            
            end_str = input("End time (HH:MM): ").strip()
            end_time = datetime.strptime(end_str, '%H:%M').time()
            
            class_name = input("Class name: ").strip()
            class_desc = input("Class description: ").strip()
            location = input("Location: ").strip()
            capacity = int(input("Capacity: ").strip())
            
            # Create schedule
            # SELECT * FROM schedule_type WHERE type = 'Group Class' LIMIT 1
            group_class_type = session.query(ScheduleType).filter_by(type='Group Class').first()
            new_schedule = Schedule(
                trainer_id=selected_trainer.id,
                date=class_date,
                start_time=start_time,
                end_time=end_time,
                type=group_class_type.id
            )
            session.add(new_schedule)
            session.flush()
            
            # Create session
            new_session = Session(
                schedule_id=new_schedule.id,
                size=capacity,
                name=class_name,
                desc=class_desc,
                location=location,
                sex_restrict='A'
            )
            session.add(new_session)
            session.commit()
            print("[SUCCESS] Class created successfully!")
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Error: {e}")
    
    elif choice == '3':
        try:
            class_id = int(input("\nClass ID to cancel: ").strip())
            # SELECT * FROM session WHERE id = ? LIMIT 1
            class_to_cancel = session.query(Session).filter_by(id=class_id).first()
            
            if class_to_cancel:
                session.delete(class_to_cancel)
                session.commit()
                print("[SUCCESS] Class cancelled successfully!")
            else:
                print("[ERROR] Class not found!")
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Error: {e}")


def process_billing(session, user):
    """Create and manage bills"""
    print("\n BILLING & PAYMENTS \n")
    
    print("\n1. Create New Bill")
    print("2. View Unpaid Bills")
    print("3. Process Payment")
    print("4. Back")
    
    choice = input("\nChoice: ").strip()
    
    if choice == '1':
        try:
            # Get member
            # SELECT * FROM role WHERE name = 'Member' LIMIT 1
            member_role = session.query(Role).filter_by(name='Member').first()
            # SELECT * FROM user WHERE role = ?
            members = session.query(User).filter_by(role=member_role.id).all()
            
            print("\nMembers:")
            for i, member in enumerate(members, 1):
                print(f"{i}. {member.first_name} {member.last_name} ({member.email})")
            
            member_choice = int(input("\nSelect member: ").strip())
            selected_member = members[member_choice - 1]
            
            # Create bill
            new_bill = Bill(
                admin_id=user.id,
                member_id=selected_member.id,
                date=date.today(),
                paid=False
            )
            session.add(new_bill)
            session.flush()
            
            # Add items
            # SELECT * FROM service
            services = session.query(Service).all()
            print("\nServices:")
            for service in services:
                print(f"{service.id}. {service.name} - ${service.price}")
            
            while True:
                service_id = input("\nService ID (0 to finish): ").strip()
                if service_id == '0':
                    break
                
                quantity = int(input("Quantity: ").strip())
                
                item = Item(
                    bill_id=new_bill.id,
                    service_id=int(service_id),
                    quantity=quantity
                )
                session.add(item)
            
            session.commit()
            print("[SUCCESS] Bill created successfully!")
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Error: {e}")
    
    elif choice == '2':
        # SELECT * FROM bill WHERE paid = FALSE
        unpaid_bills = session.query(Bill).filter_by(paid=False).all()
        
        print("\nUnpaid Bills:")
        for bill in unpaid_bills:
            total = sum(float(item.service.price) * item.quantity for item in bill.items)
            print(f"Bill #{bill.id} - {bill.member.first_name} {bill.member.last_name}")
            print(f"  Date: {bill.date}, Amount: ${total:.2f}")
    
    elif choice == '3':
        try:
            bill_id = int(input("\nBill ID to mark as paid: ").strip())
            # SELECT * FROM bill WHERE id = ? LIMIT 1
            bill = session.query(Bill).filter_by(id=bill_id).first()
            
            if bill:
                bill.paid = True
                session.commit()
                print("[SUCCESS] Payment processed successfully!")
            else:
                print("[ERROR] Bill not found!")
        except Exception as e:
            session.rollback()
            print(f"[ERROR] Error: {e}")


def admin_menu(session, user):
    """Admin main menu"""
    while True:
        print("\n ADMIN MENU \n")
        print("1. Manage Equipment")
        print("2. Manage Class Schedule")
        print("3. Process Billing")
        print("4. Logout")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            manage_equipment(session, user)
        elif choice == '2':
            manage_class_schedule(session, user)
        elif choice == '3':
            process_billing(session, user)
        elif choice == '4':
            print("\nLogging out...")
            break
        else:
            print("[ERROR] Invalid choice!")
        
        input("\nPress Enter to continue...")

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
                # Member registration
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
                    member_role = db_session.query(Role).filter_by(name='Member').first()
                    
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
                    
                    db_session.add(new_user)
                    db_session.commit()
                    print("\n[SUCCESS] Registration successful! You can now login.")
                except Exception as e:
                    db_session.rollback()
                    print(f"\n[ERROR] Registration failed: {e}")
            
            elif choice == '3':
                print("\nThank you for using the Health and Fitness Club Management System!")
                break
            
            else:
                print("\n[ERROR] Invalid choice!")
    
    finally:
        db_session.close()


if __name__ == "__main__":
    main()

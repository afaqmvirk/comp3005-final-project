# Health and Fitness Club Management System
# Trainer Functions

from datetime import datetime, date
from models import Schedule, ScheduleType, Session, Enrollment, User, Metric, Goal


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


# Raymond Liu 101264487
# Afak
# Member Functions

from datetime import datetime, date
from decimal import Decimal
from models import Metric, MetricType, Goal, Enrollment, Session, Schedule


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
            print(f"- {metric.metric_type_obj.metric_name}: {metric.value} "
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
            print(f"- Target: {metric.metric_type_obj.metric_name} = {metric.value} by {goal.goal_date}")
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
            print(f"- {enrollment.session.name} - {sched.date} at {sched.start_time}")
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
                print(f"- {metric.logged_date.strftime('%Y-%m-%d')}: {metric.value}")
            
            # Simple trend analysis
            if len(metrics) >= 2:
                first_val = float(metrics[0].value)
                last_val = float(metrics[-1].value)
                change = last_val - first_val
                if change > 0:
                    print(f"Trend: +{change:.2f} (increased)")
                elif change < 0:
                    print(f"Trend: {change:.2f} (decreased)")
                else:
                    print("Trend: No change")


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
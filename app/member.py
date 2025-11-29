# Raymond Liu 101264487
# Afaq Virk 101338854
# Member Functions

from datetime import datetime, date
from decimal import Decimal
from models import Metric, MetricType, Goal, Enrollment, Session, Schedule
from app.cli_utils import menu, header, pause, sleep, error


def member_dashboard(session, user):
    """Display member's personalized dashboard"""
    header("Member Dashboard")
    
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
    # SELECT * FROM goal JOIN metric ON goal.metric_id = metric.id WHERE metric.user_id = ?
    goals = (session.query(Goal)
             .join(Metric, Goal.metric_id == Metric.id)
             .filter(Metric.user_id == user.id)
             .all())
    if goals:
        print(f"\nActive Fitness Goals: {len(goals)}")
        for goal in goals:
            metric = goal.target_metric
            print(f"- Target: {metric.metric_type_obj.metric_name} = {metric.value} by {goal.goal_date}")
    else:
        print("\nNo fitness goals set yet.")
    
    # Upcoming enrollments
    today = date.today()

    # Past classes attended count
    past_count = (session.query(Enrollment)
                  .join(Session)
                  .join(Schedule)
                  .filter(Enrollment.member_id == user.id,
                          Schedule.date < today,
                          Enrollment.attended == True)
                  .count())
    print(f"\nPast Classes Attended: {past_count}")

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
    header("Manage Profile")
    
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
            error("Passwords don't match!")


def log_health_metrics(session, user):
    """Log new health metrics"""
    header("Log Health Metrics")
    
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
        error("Invalid input!")
    except Exception as e:
        session.rollback()
        error(f"Error: {e}")


def view_health_metrics(session, user):
    """View health metrics history with trend analysis"""
    header("Health Metrics History")
    
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

        # Check if an existing goal for this metric type exists
        existing_goal = (session.query(Goal)
                         .join(Metric, Goal.metric_id == Metric.id)
                         .filter(Metric.user_id == user.id, Metric.metric_type == metric_type_id)
                         .first())

        if existing_goal:
            print("\nA goal for this metric already exists:")
            print(f"- Current target: {existing_goal.target_metric.value} by {existing_goal.goal_date}")
            overwrite = input("Overwrite existing goal? (y/N): ").strip().lower()
            if overwrite != 'y':
                print("Keeping existing goal unchanged.")
                return

        # Create a metric entry representing the target value (used to tie goal to type/value)
        goal_metric = Metric(
            user_id=user.id,
            metric_type=metric_type_id,
            value=Decimal(str(target_value)),
            logged_date=datetime.now()
        )
        session.add(goal_metric)
        session.flush()

        if existing_goal:
            # Replace existing goal's target and date
            old_metric = existing_goal.target_metric
            existing_goal.metric_id = goal_metric.id
            existing_goal.goal_date = goal_date
            session.flush()
            # Remove the previously attached target metric row to avoid clutter
            try:
                session.delete(old_metric)
            except Exception:
                pass
        else:
            # Create a new goal
            new_goal = Goal(
                metric_id=goal_metric.id,
                goal_date=goal_date
            )
            session.add(new_goal)

        session.commit()
        print("[SUCCESS] Fitness goal saved!")
    except ValueError:
        print("[ERROR] Invalid input format!")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Error: {e}")


def view_goal_progress(session, user):
    """Display progress towards each fitness goal with latest metrics."""
    header("Goal Progress")

    goals = (session.query(Goal)
             .join(Metric, Goal.metric_id == Metric.id)
             .filter(Metric.user_id == user.id)
             .all())
    if not goals:
        print("\nNo fitness goals set yet.")
        return

    for goal in goals:
        target_metric = goal.target_metric
        metric_type_id = target_metric.metric_type
        metric_name = target_metric.metric_type_obj.metric_name
        target_val = float(target_metric.value)

        # Latest actual metric EXCLUDING the target metric row
        latest_actual = (session.query(Metric)
                         .filter(Metric.user_id == user.id,
                                 Metric.metric_type == metric_type_id,
                                 Metric.id != goal.metric_id)
                         .order_by(Metric.logged_date.desc())
                         .first())

        # Baseline value at or before goal creation (excluding the goal target row)
        baseline = (session.query(Metric)
                    .filter(Metric.user_id == user.id,
                            Metric.metric_type == metric_type_id,
                            Metric.id != goal.metric_id,
                            Metric.logged_date <= target_metric.logged_date)
                    .order_by(Metric.logged_date.desc())
                    .first())

        print(f"\n- {metric_name}")
        print(f"  Target: {target_val:.2f} by {goal.goal_date}")

        if latest_actual:
            current_val = float(latest_actual.value)
            delta = target_val - current_val
            status = "increase" if delta > 0 else ("decrease" if delta < 0 else "reach")
            print(f"  Latest: {current_val:.2f} ({latest_actual.logged_date.strftime('%Y-%m-%d')})")
            if delta != 0:
                print(f"  Remaining to {status}: {abs(delta):.2f}")
            else:
                print("  Goal value reached.")

            # Progress percentage relative to baseline, if available/meaningful
            if baseline and float(baseline.value) != target_val:
                baseline_val = float(baseline.value)
                total_needed = target_val - baseline_val
                progressed = current_val - baseline_val
                if total_needed != 0:
                    pct = max(0.0, min(1.0, progressed / total_needed)) * 100.0
                    print(f"  Progress: {pct:.0f}% since goal set (baseline {baseline_val:.2f})")
        else:
            print("  No logged metrics yet to measure progress.")


def browse_and_enroll_sessions(session, user):
    """Browse upcoming sessions and enroll if space is available."""
    header("Browse & Enroll in Sessions")

    today = date.today()
    # Upcoming sessions with schedule info
    sessions = (session.query(Session)
                .join(Schedule)
                .filter(Schedule.date >= today)
                .order_by(Schedule.date, Schedule.start_time)
                .all())

    if not sessions:
        print("\nNo upcoming sessions are available at the moment.")
        return

    print("\nAvailable Sessions:")
    rows = []
    for i, sess in enumerate(sessions, 1):
        sched = sess.schedule
        trainer = sched.trainer
        enrolled_count = len(sess.enrollments)
        spots_left = max(0, sess.size - enrolled_count)
        room_name = sess.room.name if getattr(sess, "room", None) else (sess.location or "TBA")
        print(f"{i}. {sess.name} | {sched.date} {sched.start_time}-{sched.end_time} | "
              f"Trainer: {trainer.first_name} {trainer.last_name} | "
              f"Location: {room_name} | "
              f"Capacity: {enrolled_count}/{sess.size} (Left: {spots_left})")

    try:
        choice = int(input("\nSelect a session to enroll (0 to go back): ").strip())
        if choice == 0:
            return
        if not (1 <= choice <= len(sessions)):
            error("Invalid selection!")
            return

        selected = sessions[choice - 1]
        # Duplicate enrollment check
        existing = (session.query(Enrollment)
                    .filter(Enrollment.session_id == selected.id,
                            Enrollment.member_id == user.id)
                    .first())
        if existing:
            error("You are already enrolled in this session.")
            return

        # Capacity check
        current = len(selected.enrollments)
        if current >= selected.size:
            error("This session is full.")
            return

        enrollment = Enrollment(session_id=selected.id, member_id=user.id, attended=False)
        session.add(enrollment)
        session.commit()
        print("[SUCCESS] You have been enrolled in the session!")
    except ValueError:
        error("Invalid input!")
    except Exception as e:
        session.rollback()
        error(f"Error: {e}")

def cancel_session(session, user):
    """Cancel a scheduled session"""
    header("Cancel Session")
    
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
            error("Invalid selection!")
    except ValueError:
        error("Invalid input!")
    except Exception as e:
        session.rollback()
        error(f"Error: {e}")


def member_menu(session, user):
    """Member main menu"""
    while True:
        choice = menu("Member Menu", [
            "View Dashboard",
            "Manage Profile",
            "Log Health Metrics",
            "View Health Metrics History",
            "Set Fitness Goals",
            "View Goal Progress",
            "Browse & Enroll in Sessions",
            "Cancel Session",
            "Logout",
        ])
        
        if choice == '1':
            member_dashboard(session, user)
        elif choice == '2':
            manage_profile(session, user)
        elif choice == '3':
            log_health_metrics(session, user)
        elif choice == '4':
            view_health_metrics(session, user)
        elif choice == '5':
            set_fitness_goals(session, user)
        elif choice == '6':
            view_goal_progress(session, user)
        elif choice == '7':
            browse_and_enroll_sessions(session, user)
        elif choice == '8':
            cancel_session(session, user)
        elif choice == '9':
            print("\nLogging out...")
            sleep(0.8)
            break
        else:
            error("Invalid choice!")
        
        pause()


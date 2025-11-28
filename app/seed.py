from datetime import date, time, datetime
from decimal import Decimal
from typing import Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import (
    Base,
    Role,
    User,
    Service,
    Bill,
    Item,
    MetricType,
    Metric,
    Room,
    EquipmentStatus,
    Equipment,
    ScheduleType,
    Schedule,
    Session as TrainingSession,
    Enrollment,
)


def reset_and_seed(database_url: str) -> None:
    """Drop and recreate all tables, then seed sample data via ORM."""
    engine = create_engine(database_url, echo=False)

    # Drop and recreate schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    SessionFactory = sessionmaker(bind=engine)
    db = SessionFactory()

    try:
        # Roles
        roles = {
            "Member": Role(name="Member"),
            "Trainer": Role(name="Trainer"),
            "Admin": Role(name="Admin"),
        }
        db.add_all(roles.values())

        # Schedule types
        schedule_types = {
            "Group Class": ScheduleType(type="Group Class"),
            "Personal Training": ScheduleType(type="Personal Training"),
            "Consultation": ScheduleType(type="Consultation"),
        }
        db.add_all(schedule_types.values())

        # Equipment status
        equipment_status = {
            "Available": EquipmentStatus(type="Available"),
            "In Use": EquipmentStatus(type="In Use"),
            "Maintenance": EquipmentStatus(type="Maintenance"),
            "Out of Service": EquipmentStatus(type="Out of Service"),
        }
        db.add_all(equipment_status.values())

        # Metric types
        metric_types = {
            "Weight": MetricType(metric_name="Weight", metric_desc="Body weight in pounds"),
            "Body Fat %": MetricType(metric_name="Body Fat %", metric_desc="Body fat percentage"),
            "BMI": MetricType(metric_name="BMI", metric_desc="Body Mass Index"),
            "Heart Rate": MetricType(metric_name="Heart Rate", metric_desc="Resting heart rate (bpm)"),
            "Height": MetricType(metric_name="Height", metric_desc="Height in inches"),
        }
        db.add_all(metric_types.values())

        # Services
        services = [
            Service(name="Monthly Membership", price=Decimal("49.99")),
            Service(name="Annual Membership", price=Decimal("499.99")),
            Service(name="Personal Training Session (60 min)", price=Decimal("75.00")),
            Service(name="Personal Training Package (10 sessions)", price=Decimal("650.00")),
            Service(name="Group Fitness Class Drop-In", price=Decimal("15.00")),
            Service(name="Group Fitness Class Package (10 classes)", price=Decimal("120.00")),
            Service(name="Nutritional Consultation", price=Decimal("100.00")),
            Service(name="Fitness Assessment", price=Decimal("50.00")),
            Service(name="Guest Pass (Single Day)", price=Decimal("20.00")),
            Service(name="Locker Rental (Monthly)", price=Decimal("10.00")),
        ]
        db.add_all(services)

        # Rooms
        rooms = {
            "Yoga Studio A": Room(name="Yoga Studio A", capacity=20),
            "Spin Room": Room(name="Spin Room", capacity=25),
            "Weight Training Floor": Room(name="Weight Training Floor", capacity=50),
            "Cardio Zone": Room(name="Cardio Zone", capacity=40),
            "Group Fitness Studio B": Room(name="Group Fitness Studio B", capacity=30),
            "Personal Training Room 1": Room(name="Personal Training Room 1", capacity=2),
            "Personal Training Room 2": Room(name="Personal Training Room 2", capacity=2),
            "Boxing Studio": Room(name="Boxing Studio", capacity=15),
            "Pilates Studio": Room(name="Pilates Studio", capacity=12),
            "Multi-Purpose Room": Room(name="Multi-Purpose Room", capacity=35),
        }
        db.add_all(rooms.values())

        # Ensure IDs are assigned for lookups
        db.flush()

        # Users
        admin_user = User(
            email="lebron.james@fitclub.com",
            password="admin123",
            first_name="LeBron",
            last_name="James",
            date_of_birth=date(1984, 12, 30),
            sex="M",
            phone="555-2323",
            role=roles["Admin"].id,
        )
        trainer_user = User(
            email="t1@fitclub.com",
            password="trainer123",
            first_name="Bronny",
            last_name="James",
            date_of_birth=date(1990, 5, 12),
            sex="M",
            phone="555-0201",
            role=roles["Trainer"].id,
        )
        member_user = User(
            email="steph.curry@fitclub.com",
            password="member123",
            first_name="Stephen",
            last_name="Curry",
            date_of_birth=date(1988, 3, 14),
            sex="M",
            phone="555-3030",
            role=roles["Member"].id,
        )
        db.add_all([admin_user, trainer_user, member_user])
        # Ensure user IDs are available for FK references below
        db.flush()

        # Equipment
        db.add_all([
            Equipment(name="Yoga Mat Set (20 mats)", room=rooms["Yoga Studio A"], status=equipment_status["Available"]),
            Equipment(name="Yoga Block Set", room=rooms["Yoga Studio A"], status=equipment_status["Available"]),
            Equipment(name="Resistance Band Set", room=rooms["Yoga Studio A"], status=equipment_status["Available"]),
            Equipment(name="Spin Bike 1", room=rooms["Spin Room"], status=equipment_status["Available"]),
            Equipment(name="Spin Bike 2", room=rooms["Spin Room"], status=equipment_status["Available"]),
            Equipment(name="Bench Press Station 1", room=rooms["Weight Training Floor"], status=equipment_status["Available"]),
            Equipment(name="Bench Press Station 2", room=rooms["Weight Training Floor"], status=equipment_status["Available"]),
            Equipment(name="Squat Rack 1", room=rooms["Weight Training Floor"], status=equipment_status["Available"]),
            Equipment(name="Squat Rack 2", room=rooms["Weight Training Floor"], status=equipment_status["In Use"]),
            Equipment(name="Treadmill 1", room=rooms["Cardio Zone"], status=equipment_status["Available"]),
            Equipment(name="Treadmill 2", room=rooms["Cardio Zone"], status=equipment_status["Available"]),
            Equipment(name="Heavy Bag 1", room=rooms["Boxing Studio"], status=equipment_status["Available"]),
            Equipment(name="Speed Bag", room=rooms["Boxing Studio"], status=equipment_status["Available"]),
            Equipment(name="Boxing Gloves Set", room=rooms["Boxing Studio"], status=equipment_status["Available"]),
            Equipment(name="Reformer 1", room=rooms["Pilates Studio"], status=equipment_status["Available"]),
            Equipment(name="Pilates Ball Set", room=rooms["Pilates Studio"], status=equipment_status["Available"]),
            Equipment(name="Foam Roller Set", room=rooms["Pilates Studio"], status=equipment_status["Available"]),
        ])

        # Schedules for trainer
        sched_pt = Schedule(
            trainer_id=trainer_user.id,
            date=date(2024, 12, 1),
            start_time=time(9, 0, 0),
            end_time=time(10, 0, 0),
            schedule_type_obj=schedule_types["Personal Training"],
        )
        sched_group = Schedule(
            trainer_id=trainer_user.id,
            date=date(2024, 12, 1),
            start_time=time(14, 0, 0),
            end_time=time(15, 0, 0),
            schedule_type_obj=schedule_types["Group Class"],
        )
        db.add_all([sched_pt, sched_group])
        db.flush()

        # Sessions
        sess_pt = TrainingSession(
            schedule_id=sched_pt.id,
            size=1,
            name="Personal Training",
            desc="One-on-one strength training session",
            location="Personal Training Room 1",
            sex_restrict="A",
        )
        sess_group = TrainingSession(
            schedule_id=sched_group.id,
            size=20,
            name="Basketball Skills Training",
            desc="Improve your basketball fundamentals",
            location="Multi-Purpose Room",
            sex_restrict="A",
        )
        db.add_all([sess_pt, sess_group])
        db.flush()

        # Enrollment for member
        db.add_all([
            Enrollment(session_id=sess_pt.id, member_id=member_user.id, attended=False),
            Enrollment(session_id=sess_group.id, member_id=member_user.id, attended=False),
        ])

        # Bill and items
        bill = Bill(admin_id=admin_user.id, member_id=member_user.id, date=date(2024, 11, 27), paid=False)
        db.add(bill)
        db.flush()

        service_lookup: Dict[str, Service] = {s.name: s for s in services}
        db.add_all([
            Item(bill_id=bill.id, service_id=service_lookup["Monthly Membership"].id, quantity=1),
            Item(bill_id=bill.id, service_id=service_lookup["Personal Training Session (60 min)"].id, quantity=2),
        ])

        # Metrics for member
        db.add_all([
            Metric(user_id=member_user.id, metric_type=metric_types["Height"].id, value=Decimal("75"), logged_date=datetime(2024, 11, 20, 9, 0, 0)),
            Metric(user_id=member_user.id, metric_type=metric_types["Weight"].id, value=Decimal("185"), logged_date=datetime(2024, 11, 20, 9, 0, 0)),
            Metric(user_id=member_user.id, metric_type=metric_types["Body Fat %"].id, value=Decimal("12.5"), logged_date=datetime(2024, 11, 20, 9, 0, 0)),
            Metric(user_id=member_user.id, metric_type=metric_types["Heart Rate"].id, value=Decimal("58"), logged_date=datetime(2024, 11, 20, 9, 0, 0)),
        ])

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()



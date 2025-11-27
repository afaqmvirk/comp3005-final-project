# Raymond Liu 101264487
# Afa1 Virk 101338854
# Database Models

from sqlalchemy import Column, Integer, String, Date, Time, Boolean, DECIMAL, CHAR, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

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


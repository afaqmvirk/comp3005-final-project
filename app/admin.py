# Raymond Liu 101264487
# Afak
# Admin Functions

from datetime import datetime, date
from models import Equipment, EquipmentStatus, Session, Schedule, Enrollment, Role, User, ScheduleType, Bill, Service, Item


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
            print(f"Trainer: {sched.trainer.first_name} {sched.trainer.last_name}")
            print(f"Enrolled: {enrolled}/{sess.size}")
    
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
            print(f"Date: {bill.date}, Amount: ${total:.2f}")
    
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


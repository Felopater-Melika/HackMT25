
import datetime
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, create_engine
from sqlalchemy.orm import relationship, sessionmaker

#from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import getpass  # To securely input passwords
from passlib.hash import bcrypt  # For password hashing

# Database setup
Base = declarative_base()
engine = create_engine(
    "sqlite:///sql.db",
    connect_args={"check_same_thread": False},
    echo=True  # Optional: shows SQL logging
)
Session = sessionmaker(bind=engine)
session = Session()

# Optional: Define an enumeration for medication schedule statuses
class ScheduleStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    missed = "missed"
    rescheduled = "rescheduled"

# ---------------------------
# Caregiver Model
# ---------------------------
class Caregiver(Base):
    __tablename__ = 'caregivers'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime,
                        default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
    
    # One caregiver can have many patients
    patients = relationship("Patient", back_populates="caregiver")

# ---------------------------
# Patient Model
# ---------------------------
class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True)
    caregiver_id = Column(Integer, ForeignKey('caregivers.id'))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime)
    contact_info = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime,
                        default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
    
    # Relationship to caregiver
    caregiver = relationship("Caregiver", back_populates="patients")
    # A patient can have multiple patient-medication entries
    patient_medications = relationship("PatientMedication", back_populates="patient")
    # A patient can have multiple call logs
    call_logs = relationship("CallLog", back_populates="patient")

# ---------------------------
# Medication Model
# ---------------------------
class Medication(Base):
    __tablename__ = 'medications'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    manufacturer = Column(String(255))
    side_effects = Column(Text)
    
    # Back-reference from PatientMedication
    patient_medications = relationship("PatientMedication", back_populates="medication")

# ---------------------------
# PatientMedication Model
# (Associates Patients with Medications)
# ---------------------------
class PatientMedication(Base):
    __tablename__ = 'patient_medications'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    medication_id = Column(Integer, ForeignKey('medications.id'))
    dosage = Column(String(100))         # e.g., "500 mg"
    frequency = Column(String(100))      # e.g., "twice a day"
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)  # Could be null if ongoing
    instructions = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime,
                        default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
    
    # Relationships to patient and medication
    patient = relationship("Patient", back_populates="patient_medications")
    medication = relationship("Medication", back_populates="patient_medications")
    # One patient-medication can have multiple scheduled doses
    medication_schedules = relationship("MedicationSchedule", back_populates="patient_medication")

# ---------------------------
# MedicationSchedule Model
# ---------------------------
class MedicationSchedule(Base):
    __tablename__ = 'medication_schedules'
    
    id = Column(Integer, primary_key=True)
    patient_medication_id = Column(Integer, ForeignKey('patient_medications.id'))
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.pending)
    confirmation_time = Column(DateTime, nullable=True)
    updated_at = Column(DateTime,
                        default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
    
    # Relationship to patient medication and call logs
    patient_medication = relationship("PatientMedication", back_populates="medication_schedules")
    call_logs = relationship("CallLog", back_populates="medication_schedule")

# ---------------------------
# CallLog Model
# ---------------------------
class CallLog(Base):
    __tablename__ = 'call_logs'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    schedule_id = Column(Integer, ForeignKey('medication_schedules.id'))
    call_time = Column(DateTime, default=datetime.datetime.utcnow)
    call_status = Column(String(50))  # e.g., "answered", "no response", "failed"
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    medication_schedule = relationship("MedicationSchedule", back_populates="call_logs")
    patient = relationship("Patient", back_populates="call_logs")

# Create the tables
#Base.metadata.create_all(engine)

# Function to add caregiver
def caregiver_register():
    username = input("Enter username: ")
    email = input("Enter email: ")
    
    # Secure password input
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    if password != confirm_password:
        print("Passwords do not match.")
        return

    # Hash the password before storing
    hashed_password = bcrypt.hash(password)

    # Check if email or username already exists
    if session.query(Caregiver).filter((Caregiver.email == email) | (Caregiver.username == username)).first():
        print("Username or email already exists.")
        return

    # Add new caregiver
    new_caregiver = Caregiver(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    
    session.add(new_caregiver)
    session.commit()
    print(f"Caregiver '{username}' added successfully!")

def caregiver_authenticate(email, password):
    caregiver = session.query(Caregiver).filter_by(email=email).first()
    if caregiver:
        if bcrypt.verify(password, caregiver.hashed_password):
            print("Login successful!")
            return caregiver  # Returning caregiver object for further operations
        else:
            print("Incorrect password.")
    else:
        print("Email not found.")

def caregiver_login():
    # Input from user
    email_input = input("Enter your email: ")
    password_input = input("Enter your password: ")

    # Login attempt
    logged_in_caregiver = caregiver_authenticate(email_input, password_input)



# Main loop
if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")

    while True:
        print("\n1. Login\n2. Register\n3. Exit")
        choice = input("Choose an option: ")
        
        if choice == '1':
            caregiver_login()
        elif choice == '2':
            caregiver_register()
        elif choice == '3':
            break
        else:
            print("Invalid option. Try again.")
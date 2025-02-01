# models.py
import datetime
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from config import Base, engine, SessionLocal  # Import config objects

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

# ---------------------------
# Create the Database Tables
# ---------------------------
if __name__ == '__main__':
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")
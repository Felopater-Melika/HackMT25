from database import Base, engine

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, Float
import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

# ---------------------------
# Enum for Call and Medication Schedule Status
# ---------------------------
class CallScheduleStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    missed = "missed"
    rescheduled = "rescheduled"

class MedicationScheduleStatus(enum.Enum):
    active = "active"
    inactive = "inactive"

class MedicationLogStatus(enum.Enum):
    taken = "taken"
    skipped = "skipped"
    delayed = "delayed"

# ---------------------------
# Caregiver Model
# ---------------------------
class Caregiver(Base):
    __tablename__ = "caregivers"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    #created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    #updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    patient_id = Column(Integer, ForeignKey('patients.id'))
    #patient = relationship("Patient", back_populates="caregiver", uselist=False)

# ---------------------------
# Patient Model
# ---------------------------
class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    bio = Column(Text, nullable=True)
    #created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    #updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    #caregiver_id = Column(Integer, ForeignKey('caregivers.id'))
    #caregiver = relationship("Caregiver", back_populates="patient", uselist=False)
    patient_medications = relationship("Prescription", back_populates="patient")
    medication_logs = relationship("MedicationLog", back_populates="patient")
    call_logs = relationship("CallLog", back_populates="patient")

# ---------------------------
# Prescription Model (Patient Medications)
# ---------------------------
class Prescription(Base):
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    nick = Column(String(100), nullable=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    method = Column(String(100), nullable=False)  # Example: "Oral", "Injection"
    dosage = Column(Float, nullable=False)  # Allows decimal values
    units = Column(String(50), nullable=False)  # Example: "mg", "ml"
    frequency = Column(Integer, nullable=False)  # Times per day
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # Some prescriptions are ongoing
    instructions = Column(Text, nullable=True)

    #created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    #updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="patient_medications")
    medication_schedules = relationship("MedicationSchedule", back_populates="prescription")

# ---------------------------
# MedicationSchedule Model
# ---------------------------
class MedicationSchedule(Base):
    __tablename__ = "medication_schedules"
    
    id = Column(Integer, primary_key=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(Enum(MedicationScheduleStatus), default=MedicationScheduleStatus.active, nullable=False)

    #updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    prescription = relationship("Prescription", back_populates="medication_schedules", uselist=False)
    medication_logs = relationship("MedicationLog", back_populates="medication_schedule", uselist=False)
'''
# ---------------------------
# Medication
# ---------------------------
class Medication(Base):
    __tablename__ = "medication"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    description = Column(String(255), nullable=False)
'''
# ---------------------------
# MedicationLog Model (Tracks Patient Medication Intake)
# ---------------------------
class MedicationLog(Base):
    __tablename__ = "medication_logs"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    medication_schedule_id = Column(Integer, ForeignKey("medication_schedules.id"), nullable=False)
    call_log_id = Column(Integer, ForeignKey("call_logs.id"), nullable=True)  # Links to a call, if applicable
    
    status = Column(Enum(MedicationLogStatus), default=MedicationLogStatus.taken, nullable=False)

    patient = relationship("Patient", back_populates="medication_logs")
    medication_schedule = relationship("MedicationSchedule", back_populates="medication_logs")
    call_log = relationship("CallLog", back_populates="medication_logs")

# ---------------------------
# Scheduled Calls Model
# ---------------------------
class ScheduledCalls(Base):
    __tablename__ = "scheduled_calls"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    call_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

# ---------------------------
# CallLog Model
# ---------------------------
class CallLog(Base):
    __tablename__ = "call_logs"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    call_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    call_status = Column(Enum(CallScheduleStatus), default=CallScheduleStatus.pending, nullable=False)
    transcription = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    alert = Column(Text, nullable=True)
    follow_up = Column(Text, nullable=True)

    #created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    patient = relationship("Patient", back_populates="call_logs")
    medication_logs = relationship("MedicationLog", back_populates="call_log")

# Create the database tables
Base.metadata.create_all(bind=engine)
from database import Base, engine

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, Float
import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

# ---------------------------
# Enums
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
    fk_patient_id = Column(Integer)  # ForeignKey placeholder

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

# ---------------------------
# Prescription Model
# ---------------------------
class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    nick = Column(String(100), nullable=True)
    fk_patient_id = Column(Integer)  # ForeignKey placeholder
    method = Column(String(100), nullable=False)
    dosage = Column(Float, nullable=False)
    units = Column(String(50), nullable=False)
    frequency = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    instructions = Column(Text, nullable=True)

# ---------------------------
# MedicationSchedule Model
# ---------------------------
class MedicationSchedule(Base):
    __tablename__ = "medication_schedules"

    id = Column(Integer, primary_key=True)
    fk_prescription_id = Column(Integer)  # ForeignKey placeholder
    fk_patient_id = Column(Integer)  # ForeignKey placeholder
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(Enum(MedicationScheduleStatus), default=MedicationScheduleStatus.active, nullable=False)

# ---------------------------
# MedicationLog Model
# ---------------------------
class MedicationLog(Base):
    __tablename__ = "medication_logs"

    id = Column(Integer, primary_key=True)
    fk_patient_id = Column(Integer)  # ForeignKey placeholder
    fk_medication_schedule_id = Column(Integer)  # ForeignKey placeholder
    fk_call_log_id = Column(Integer)  # ForeignKey placeholder
    status = Column(Enum(MedicationLogStatus), default=MedicationLogStatus.taken, nullable=False)

# ---------------------------
# Scheduled Calls Model
# ---------------------------
class ScheduledCalls(Base):
    __tablename__ = "scheduled_calls"

    id = Column(Integer, primary_key=True)
    fk_patient_id = Column(Integer)  # ForeignKey placeholder
    call_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

# ---------------------------
# CallLog Model
# ---------------------------
class CallLog(Base):
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True)
    fk_patient_id = Column(Integer)  # ForeignKey placeholder
    call_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    call_status = Column(Enum(CallScheduleStatus), default=CallScheduleStatus.pending, nullable=False)
    transcription = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    alert = Column(Text, nullable=True)
    follow_up = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)
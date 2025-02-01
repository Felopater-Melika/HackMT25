import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, Float, Table
import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ---------------------------
# Enum for Roles, Call Schedule, and Medication Schedule
# ---------------------------
class UserRole(enum.Enum):
    patient = "patient"
    caregiver = "caregiver"

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
# Many-to-Many Relationship: Caregivers & Patients
# ---------------------------
caregiver_patient_association = Table(
    "caregiver_patient_association",
    Base.metadata,
    Column("caregiver_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("patient_id", Integer, ForeignKey("users.id"), primary_key=True)
)

# ---------------------------
# Unified User Model (Patients & Caregivers)
# ---------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)  # ✅ Differentiates patient & caregiver
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Many-to-Many Relationship (Only applicable for caregivers managing patients)
    patients = relationship(
        "User",
        secondary=caregiver_patient_association,
        primaryjoin=id == caregiver_patient_association.c.caregiver_id,
        secondaryjoin=id == caregiver_patient_association.c.patient_id,
        back_populates="caregivers"
    )
    
    caregivers = relationship(
        "User",
        secondary=caregiver_patient_association,
        primaryjoin=id == caregiver_patient_association.c.patient_id,
        secondaryjoin=id == caregiver_patient_association.c.caregiver_id,
        back_populates="patients"
    )

    # One-to-Many Relationships
    prescriptions = relationship("Prescription", back_populates="patient")
    medication_logs = relationship("MedicationLog", back_populates="patient")
    call_logs = relationship("CallLog", back_populates="patient")

# ---------------------------
# Prescription Model (Patient Medications)
# ---------------------------
class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    method = Column(String(100), nullable=False)  # Example: "Oral", "Injection"
    dosage = Column(Float, nullable=False)  # Allows decimal values
    units = Column(String(50), nullable=False)  # Example: "mg", "ml"
    frequency = Column(Integer, nullable=False)  # Times per day

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)  # Some prescriptions are ongoing
    instructions = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    patient = relationship("User", back_populates="prescriptions")
    medication_schedules = relationship("MedicationSchedule", back_populates="prescription")

# ---------------------------
# MedicationSchedule Model
# ---------------------------
class MedicationSchedule(Base):
    __tablename__ = "medication_schedules"

    id = Column(Integer, primary_key=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)

    scheduled_time = Column(DateTime, nullable=False)
    status = Column(Enum(MedicationScheduleStatus), default=MedicationScheduleStatus.active, nullable=False)
    confirmation_time = Column(DateTime, nullable=True)

    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    prescription = relationship("Prescription", back_populates="medication_schedules")
    medication_logs = relationship("MedicationLog", back_populates="medication_schedule")

# ---------------------------
# MedicationLog Model (Tracks Patient Medication Intake)
# ---------------------------
class MedicationLog(Base):
    __tablename__ = "medication_logs"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medication_schedule_id = Column(Integer, ForeignKey("medication_schedules.id"), nullable=False)
    call_log_id = Column(Integer, ForeignKey("call_logs.id"), nullable=True)  # Links to a call, if applicable

    status = Column(Enum(MedicationLogStatus), default=MedicationLogStatus.taken, nullable=False)

    patient = relationship("User", back_populates="medication_logs")
    medication_schedule = relationship("MedicationSchedule", back_populates="medication_logs")
    call_log = relationship("CallLog", back_populates="medication_logs")

# ---------------------------
# CallLog Model
# ---------------------------
class CallLog(Base):
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    call_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    call_status = Column(Enum(CallScheduleStatus), default=CallScheduleStatus.pending, nullable=False)
    transcription = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    alert = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    patient = relationship("User", back_populates="call_logs")
    medication_logs = relationship("MedicationLog", back_populates="call_log")
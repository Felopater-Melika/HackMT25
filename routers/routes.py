from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from datetime import datetime
from models import MedicationSchedule, Prescription, MedicationScheduleStatus, Patient, ScheduledCalls, Caregiver, CallScheduleStatus, CallLog, MedicationSchedule
from typing import Optional
import random

router = APIRouter()

# Patient stuff
class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    bio: str

# Caregiver stuff
class CaregiverCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: str
    password: str
    confirm_password: str
    patient: PatientCreate

class CaregiverLogin(BaseModel):
    email: str
    password: str

# Prescription Creation stuff
class PrescriptionCreate(BaseModel):
    name: str
    nick: str
    patient_id: int
    method: str
    dosage: float
    units: str
    frequency: int
    start_date: datetime
    end_date: Optional[datetime] = None
    instructions: Optional[str] = None

# Medication Scheduling stuff
class MedicationScheduleCreate(BaseModel):
    prescription_id: int
    scheduled_time: datetime
    status: MedicationScheduleStatus = MedicationScheduleStatus.active

# Medication stuff
class MedicationCreate(BaseModel):
    name: str
    description: str

# Scheduled Calls
class CreateScheduledCall(BaseModel):
    patient_id: int
    call_time: datetime

class GetScheduledCalls(BaseModel):
    patient_id: int

# CallLog Create
class CallLogCreate(BaseModel):
    patient_id: int
    call_time: Optional[datetime] = None
    call_status: CallScheduleStatus = CallScheduleStatus.pending
    transcription: Optional[str] = None
    summary: Optional[str] = None
    alert: Optional[str] = None
    follow_up: Optional[str] = None

# Register Caregiver
@router.post("/register/")
def register_caregiver(caregiver: CaregiverCreate, db: Session = Depends(get_db)):
    if caregiver.password != caregiver.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    if db.query(Caregiver).filter(Caregiver.email == caregiver.email).first():
        raise HTTPException(status_code=400, detail="Email already exists.")
    # Create patient (DB assigns unique ID)
    new_patient = Patient(
        first_name=caregiver.patient.first_name,
        last_name=caregiver.patient.last_name,
        phone_number=caregiver.patient.phone_number,
        bio=caregiver.patient.bio
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    # Create caregiver linked to patient via fk_patient_id
    new_caregiver = Caregiver(
        first_name=caregiver.first_name,
        last_name=caregiver.last_name,
        email=caregiver.email,
        phone_number=caregiver.phone_number,
        password=caregiver.password,  # Plain text per request
        fk_patient_id=new_patient.id
    )
    db.add(new_caregiver)
    db.commit()
    db.refresh(new_caregiver)
    return new_caregiver

@router.post("/patients/", response_model=PatientCreate)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    db_patient = Patient(
        first_name=patient.first_name,
        last_name=patient.last_name,
        phone_number=patient.phone_number
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.post("/patients/prescriptions/")
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db)):
    db_prescription = Prescription(
        name=prescription.name,
        nick=prescription.nick,
        fk_patient_id=prescription.patient_id,
        method=prescription.method,
        dosage=prescription.dosage,
        units=prescription.units,
        frequency=prescription.frequency,
        start_date=prescription.start_date,
        end_date=prescription.end_date,
        instructions=prescription.instructions
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

@router.post("/medication-schedules/")
def create_medication_schedule(schedule: MedicationScheduleCreate, db: Session = Depends(get_db)):
    # Fetch prescription and extract its fk_patient_id
    prescription = db.query(Prescription).filter(Prescription.id == schedule.prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    patient_id_value = getattr(prescription, "fk_patient_id", None)
    if not isinstance(patient_id_value, int):
        raise HTTPException(status_code=500, detail="Invalid patient_id type on prescription")
    # Create schedule using fk_prescription_id and fk_patient_id
    new_schedule = MedicationSchedule(
        fk_prescription_id=schedule.prescription_id,
        scheduled_time=schedule.scheduled_time,
        status=schedule.status,
        fk_patient_id=patient_id_value
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule

@router.post("/patients/scheduled-calls/")
def create_scheduled_call(scheduled_calls: CreateScheduledCall, db: Session = Depends(get_db)):
    new_schedule = ScheduledCalls(
        fk_patient_id=scheduled_calls.patient_id,
        call_time=scheduled_calls.call_time
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule

@router.post("/patients/call-logs/")
def create_call_log(call_log: CallLogCreate, db: Session = Depends(get_db)):
    new_call_log = CallLog(
        fk_patient_id=call_log.patient_id,
        call_time=call_log.call_time or datetime.utcnow(),
        call_status=call_log.call_status,
        transcription=call_log.transcription,
        summary=call_log.summary,
        alert=call_log.alert,
        follow_up=call_log.follow_up
    )
    db.add(new_call_log)
    db.commit()
    db.refresh(new_call_log)
    return new_call_log

@router.post("/login/")
def login_caregiver(caregiver: CaregiverLogin, db: Session = Depends(get_db)):
    db_caregiver = db.query(Caregiver).filter(Caregiver.email == caregiver.email).first()
    if not db_caregiver or db_caregiver.password != caregiver.password:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    return {
        "caregiver_id": db_caregiver.id,
        "first_name": db_caregiver.first_name,
        "last_name": db_caregiver.last_name,
        "email": db_caregiver.email,
        "patient_id": db_caregiver.fk_patient_id
    }

@router.get("/patients/{patient_id}")
def get_patient_details(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    prescriptions = db.query(Prescription).filter(Prescription.fk_patient_id == patient_id).all()
    medication_schedules = db.query(MedicationSchedule).filter(MedicationSchedule.fk_patient_id == patient_id).all()
    scheduled_calls = db.query(ScheduledCalls).filter(ScheduledCalls.fk_patient_id == patient_id).all()
    call_logs = db.query(CallLog).filter(CallLog.fk_patient_id == patient_id).all()
    return {
        "patient": patient,
        "prescriptions": prescriptions,
        "medication_schedules": medication_schedules,
        "scheduled_calls": scheduled_calls,
        "call_logs": call_logs,
    }

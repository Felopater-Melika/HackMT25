from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from pydantic import BaseModel
from database import get_db
from datetime import datetime
from models import MedicationSchedule, Prescription, MedicationScheduleStatus, Patient, Medication, ScheduledCalls, Caregiver, CallScheduleStatus, CallLog, MedicationSchedule
from typing import Optional
import random

router = APIRouter()

# Patient stuff
class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str

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
    dosage_per_day: int
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

# Register Caregiver
@router.post("/register/")
def register_caregiver(caregiver: CaregiverCreate, db: Session = Depends(get_db)):
    if caregiver.password != caregiver.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    hashed_password = bcrypt.hash(caregiver.password)
    db_caregiver = db.query(Caregiver).filter(
        (Caregiver.email == caregiver.email)
    ).first()

    if db_caregiver:
        raise HTTPException(status_code=400, detail="email already exists.")

    patient_id = random.randint(1000, 9999)
    new_patient = Patient(
        first_name=caregiver.patient.first_name,
        last_name=caregiver.patient.last_name,
        phone_number=caregiver.patient.phone_number,
        id=patient_id
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    new_caregiver = Caregiver(
        first_name=caregiver.first_name,
        last_name=caregiver.last_name,
        email=caregiver.email,
        phone_number=caregiver.phone_number,
        hashed_password=hashed_password,
        patient_id=patient_id
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

@router.post("/patients/{patient_id}/prescriptions/")
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db)):
    db_prescription = Prescription(
        name=prescription.name,
        nick=prescription.nick,
        patient_id=prescription.patient_id,
        method=prescription.method,
        dosage=prescription.dosage,
        units=prescription.units,
        frequency=prescription.frequency,
        start_date=prescription.start_date,
        end_date=prescription.end_date,
        instructions=prescription.instructions,
        #created_at=datetime.utcnow(),
        #updated_at=datetime.utcnow()
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

# Make new schedule
@router.post("/medication-schedules/")
def create_medication_schedule(schedule: MedicationScheduleCreate, db: Session = Depends(get_db)):
    # Check if prescription exists
    prescription = db.query(Prescription).filter(Prescription.id == schedule.prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Create new medication schedule
    new_schedule = MedicationSchedule(
        prescription_id=schedule.prescription_id,
        scheduled_time=schedule.scheduled_time,
        status=schedule.status
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    return new_schedule

@router.post("/medications/", response_model=MedicationCreate)
def create_medication(medication: MedicationCreate, db: Session = Depends(get_db)):
    db_medication = Medication(
        name=medication.name,
        description=medication.description,
    )
    db.add(db_medication)
    db.commit()
    db.refresh(db_medication)
    return db_medication

@router.post("/patients/{patient_id}/scheduled-calls/")
def create_scheduled_call(scheduled_calls: CreateScheduledCall, db: Session = Depends(get_db)):
    # Check if schedule exists
    #db_scheduled_calls = db.query(ScheduledCalls).filter(ScheduledCalls.id == scheduled_calls.id).first()
    #if db_scheduled_calls:
    #    raise HTTPException(status_code=404, detail="Scheduled call already exists")

    # Create new scheduled call
    new_schedule = ScheduledCalls(
        patient_id=scheduled_calls.patient_id,
        call_time=scheduled_calls.call_time
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule

@router.post("/patients/{patient_id}/call-logs/")
def create_call_log(call_log: CallLogCreate, db: Session = Depends(get_db)):
    new_call_log = CallLog(
        patient_id=call_log.patient_id,
        call_time=call_log.call_time or datetime.utcnow(),
        call_status=call_log.call_status,
        transcription=call_log.transcription,
        summary=call_log.summary,
        alert=call_log.alert
    )
    db.add(new_call_log)
    db.commit()
    db.refresh(new_call_log)
    return new_call_log

#
# GET
#

# Login Caregiver
@router.post("/login/")
def login_caregiver(caregiver: CaregiverLogin, db: Session = Depends(get_db)):
    db_caregiver = db.query(Caregiver).filter(Caregiver.email == caregiver.email).first()
    if not db_caregiver or not bcrypt.verify(caregiver.password, db_caregiver.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    return db_caregiver

# Scheduled Calls
@router.get("/patients/{patient_id}/scheduled-calls/")
def get_scheduled_calls(patient_id: int, db: Session = Depends(get_db)):
    # Fetch scheduled calls for the patient
    db_scheduled_calls = db.query(ScheduledCalls).filter(ScheduledCalls.patient_id == patient_id).all()
    
    if not db_scheduled_calls:
        raise HTTPException(status_code=404, detail="No scheduled calls found for this patient")

    return db_scheduled_calls  # Returns a list of scheduled calls

@router.get("/patients/{patient_id}")
def get_patient_by_id(patient_id: int, db: Session = Depends(get_db)):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.get("/patients/{patient_id}/call-logs/")
def get_call_logs(patient_id: int, db: Session = Depends(get_db)):
    call_logs = db.query(CallLog).filter(CallLog.patient_id == patient_id).all()
    return call_logs

@router.get("/patients/{patient_id}/prescriptions/")
def get_prescriptions(patient_id: int, db: Session = Depends(get_db)):
    prescriptions = db.query(Prescription).filter(Prescription.patient_id == patient_id).all()
    return prescriptions
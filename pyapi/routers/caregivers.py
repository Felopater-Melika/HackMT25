from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from pydantic import BaseModel
from database import get_db
from datetime import datetime
from models import MedicationSchedule, Prescription, MedicationScheduleStatus, Patient, Medication, ScheduledCalls, Caregiver
from typing import Optional
import random

router = APIRouter(prefix="/caregivers", tags=["Caregivers"])

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

# Register Caregiver
@router.post("/register")
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

    return {"message": f"Caregiver '{new_caregiver.first_name}' registered successfully!"}

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

@router.post("/prescriptions/")
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db)):
    db_prescription = Prescription(
        name=prescription.name,
        patient_id=prescription.patient_id,
        method=prescription.method,
        dosage=prescription.dosage,
        units=prescription.units,
        frequency=prescription.frequency,
        start_date=prescription.start_date,
        end_date=prescription.end_date,
        instructions=prescription.instructions,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

# Make new schedule
@router.post("/medication-schedules/", response_model=dict)
def create_medication_schedule(schedule: MedicationScheduleCreate, db: Session = Depends(get_db)):
    # Check if prescription exists
    prescription = db.query(Prescription).filter(Prescription.id == schedule.prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Create new medication schedule
    new_schedule = MedicationSchedule(
        prescription_id=schedule.prescription_id,
        scheduled_time=schedule.scheduled_time,
        status=schedule.status,
        updated_at=datetime.datetime.utcnow()
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    return {"message": "Medication schedule created successfully", "id": new_schedule.id}

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

@router.post("/scheduled-calls/")
def create_scheduled_call(scheduled_call: CreateScheduledCall, db: Session = Depends(get_db)):
    # Check if schedule exists
    db_scheduled_call = db.query(ScheduledCalls).filter(ScheduledCalls.id == scheduled_call.id).first()
    if db_scheduled_call:
        raise HTTPException(status_code=404, detail="Scheduled call already exists")
    
    # Create new scheduled call
    new_schedule = ScheduledCalls(
        patient_id=scheduled_call.id,
        call_time=scheduled_call.call_time
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return {"successful"}

#
# GET
#

# Login Caregiver
@router.post("/login/")
def login_caregiver(caregiver: CaregiverLogin, db: Session = Depends(get_db)):
    db_caregiver = db.query(Caregiver).filter(Caregiver.email == caregiver.email).first()
    if not db_caregiver or not bcrypt.verify(caregiver.password, db_caregiver.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    return {"message": f"Login successful for {db_caregiver.first_name}!", "id": db_caregiver.id}

# Scheduled Calls
@router.post("/scheduled-calls/")
def get_scheduled_calls(scheduled_calls: GetScheduledCalls, db: Session = Depends(get_db)):
    # Check if schedule exists
    db_scheduled_call = db.query(ScheduledCalls).filter(ScheduledCalls.id == scheduled_calls.id).first()
    if not db_scheduled_call:
        raise HTTPException(status_code=404, detail="Scheduled call not found")

    return {"id": db_scheduled_call.id, "patient_id": db_scheduled_call.patient_id, "call_time": db_scheduled_call.call_time}
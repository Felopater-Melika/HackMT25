from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from pydantic import BaseModel
from models import Caregiver
from database import get_db
from datetime import datetime
from models import MedicationSchedule, Prescription, MedicationScheduleStatus, Patient, Medication
from typing import Optional

router = APIRouter(prefix="/caregivers", tags=["Caregivers"])

# Caregiver stuff
class CaregiverCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: str
    password: str
    confirm_password: str

class CaregiverLogin(BaseModel):
    email: str
    password: str

# Patient stuff
class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str

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

    new_caregiver = Caregiver(
        first_name=caregiver.first_name,
        last_name=caregiver.last_name,
        email=caregiver.email,
        phone_number=caregiver.phone_number,
        hashed_password=hashed_password
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
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
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
        updated_at=datetime.utcnow()
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

# Login Caregiver
@router.post("/login")
def login_caregiver(caregiver: CaregiverLogin, db: Session = Depends(get_db)):
    db_caregiver = db.query(Caregiver).filter(Caregiver.email == caregiver.email).first()
    if not db_caregiver or not bcrypt.verify(caregiver.password, db_caregiver.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    return {"message": f"Login successful for {db_caregiver.first_name}!"}
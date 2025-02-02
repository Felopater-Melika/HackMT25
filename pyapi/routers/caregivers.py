from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from pydantic import BaseModel
from models import Caregiver
from database import get_db

router = APIRouter(prefix="/caregivers", tags=["Caregivers"])

# Pydantic Schemas
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

# Login Caregiver
@router.post("/login")
def login_caregiver(caregiver: CaregiverLogin, db: Session = Depends(get_db)):
    db_caregiver = db.query(Caregiver).filter(Caregiver.email == caregiver.email).first()
    if not db_caregiver or not bcrypt.verify(caregiver.password, db_caregiver.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    return {"message": f"Login successful for {db_caregiver.first_name}!"}
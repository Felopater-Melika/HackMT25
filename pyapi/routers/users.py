from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from pydantic import BaseModel, EmailStr
from models import User, UserRole
from database import get_db

router = APIRouter(prefix="/caregivers", tags=["Caregivers"])

# Pydantic Schemas
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str
    confirm_password: str
    role: UserRole  # Role: "patient" or "caregiver"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Register User
@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    # Check if email is already in use
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered.")

    hashed_password = bcrypt.hash(user.password)

    # Create a new user
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number,
        hashed_password=hashed_password,
        role=user.role.value
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": f"User '{new_user.first_name} {new_user.last_name}' registered successfully as a {new_user.role}!"}

# Login Caregiver
@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not bcrypt.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    return {"message": f"Login successful for {db_user.first_name} {db_user.last_name} ({db_user.role})!"}
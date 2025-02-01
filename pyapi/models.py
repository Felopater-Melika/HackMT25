import datetime
import enum
import getpass
import sys
import subprocess
from sqlalchemy import Column, Integer, String, DateTime, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.hash import bcrypt
import requests
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Database setup
DATABASE_URL = "sqlite:///./sql.db"
Base = declarative_base()

# SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Caregiver model
class Caregiver(Base):
    __tablename__ = 'caregivers'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # One caregiver can have many patients
    patients = relationship("Patient", back_populates="caregiver")

# Patient model
class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True, index=True)
    caregiver_id = Column(Integer, ForeignKey('caregivers.id'))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime)
    contact_info = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    caregiver = relationship("Caregiver", back_populates="patients")

# Pydantic schemas
class CaregiverCreate(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str

class CaregiverLogin(BaseModel):
    email: str
    password: str

# FastAPI app
app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register a new caregiver
@app.post("/caregivers/register")
def register_caregiver(caregiver: CaregiverCreate, db: Session = Depends(get_db)):
    if caregiver.password != caregiver.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    
    # Hash the password
    hashed_password = bcrypt.hash(caregiver.password)

    # Check if username or email exists
    db_caregiver = db.query(Caregiver).filter((Caregiver.email == caregiver.email) | (Caregiver.username == caregiver.username)).first()
    if db_caregiver:
        raise HTTPException(status_code=400, detail="Username or email already exists.")
    
    # Create new caregiver
    new_caregiver = Caregiver(
        username=caregiver.username,
        email=caregiver.email,
        hashed_password=hashed_password
    )
    
    db.add(new_caregiver)
    db.commit()
    db.refresh(new_caregiver)
    
    return {"message": f"Caregiver '{new_caregiver.username}' registered successfully!"}

# Login a caregiver
@app.post("/caregivers/login")
def login_caregiver(caregiver: CaregiverLogin, db: Session = Depends(get_db)):
    db_caregiver = db.query(Caregiver).filter(Caregiver.email == caregiver.email).first()
    if not db_caregiver or not bcrypt.verify(caregiver.password, db_caregiver.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    
    return {"message": f"Login successful for {db_caregiver.username}!"}

# Create the database tables
Base.metadata.create_all(bind=engine)

# Function to run uvicorn automatically
def run_uvicorn():
    """Run the Uvicorn server programmatically."""
    subprocess.run([sys.executable, "-m", "uvicorn", "models:app", "--reload"])

# Main loop to interact with the user (for testing purposes)
def main():
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            register_caregiver()
        elif choice == '2':
            login_caregiver()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Run the FastAPI app using uvicorn
    run_uvicorn()
    
    # Interact with the user for registration/login
    main()
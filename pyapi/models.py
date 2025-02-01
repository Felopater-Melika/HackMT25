import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Caregiver(Base):
    __tablename__ = 'caregivers'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    patients = relationship("Patient", back_populates="caregiver")

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
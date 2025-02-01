from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///caregiver_app.db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = session
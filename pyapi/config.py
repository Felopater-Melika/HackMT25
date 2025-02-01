# config.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define your database URL; here we use SQLite as an example.
SQLALCHEMY_DATABASE_URL = "sqlite:///./caregiver_app.db"

# Create the engine.
# For SQLite, include connect_args if necessary.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Optional: shows SQL logging
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the base class for our models.
Base = declarative_base()
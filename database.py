from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DEBUG_MODE = True

# Define the database file path
db_file = './sql.db'

# Step 1: Delete the existing database file if it exists
# if os.path.exists(db_file) & DEBUG_MODE:
#     os.remove(db_file)
#     print(f"Deleted existing database: {db_file}")

DATABASE_URL = "sqlite:///./sql.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
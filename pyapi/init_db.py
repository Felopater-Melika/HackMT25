from config import engine, Base
from models import *

# Create all tables in the database
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")


from fastapi import FastAPI
from database import Base, engine
from routers import caregivers

# Create the database tables
Base.metadata.create_all(bind=engine)

# FastAPI app initialization
app = FastAPI()

# Include the Caregiver router
app.include_router(caregivers.router)
from fastapi import FastAPI
from database import Base, engine
from routers import users
from fastapi.middleware.cors import CORSMiddleware

# Create the database tables
Base.metadata.create_all(bind=engine)

# FastAPI app initialization
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # FRONT END SERVER'S PORT! MAKE IT DIFFERENT HOLY SHIT
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the Caregiver router
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "FastAPI is running!"}
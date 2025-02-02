from fastapi import FastAPI
from services.twiliogpt import router as twiliogpt_router
from loguru import logger
from datetime import datetime
import os
from fastapi.middleware.cors import CORSMiddleware

from routers import routes

# FastAPI app initialization
app = FastAPI()
# logger config. To use just run logger.info("message")

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
logger.add(log_file, format="{time} {level} {message}", level="INFO")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # FRONT END SERVER'S PORT! MAKE IT DIFFERENT HOLY SHIT
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the Caregiver router
app.include_router(routes.router)

@app.get("/")
async def root():
    return {"message": "FastAPI is running!"}

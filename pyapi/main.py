from fastapi import FastAPI
from endpoints.users import router as users_router
from loguru import logger
from datetime import datetime
import os

# from endpoints.items import router as items_router
app = FastAPI()
# logger config. To use just run logger.info("message")
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
logger.add(log_file, format="{time} {level} {message}", level="INFO")


# Include routers
app.include_router(users_router)
# app.include_router(items_router)

@app.get("/")
async def root():
    return {"message": "Hello Buddy!"}

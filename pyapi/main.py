from fastapi import FastAPI
from routers import routes
from fastapi.middleware.cors import CORSMiddleware

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
app.include_router(routes.router)

@app.get("/")
async def root():
    return {"message": "FastAPI is running!"}

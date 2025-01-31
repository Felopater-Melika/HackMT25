from fastapi import FastAPI
from endpoints.users import router as users_router
# from endpoints.items import router as items_router

app = FastAPI()

# Include routers
app.include_router(users_router)
# app.include_router(items_router)

@app.get("/")
async def root():
    return {"message": "Hello Buddy!"}

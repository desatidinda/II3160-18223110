from fastapi import FastAPI
from manajemen_parkir.api.endpoints import router as parking_router
from manajemen_parkir.api.users import router as users_router

app = FastAPI(title="II3160 Smart Parking System", version="0.1.0")
app.include_router(parking_router, prefix="/api")
app.include_router(users_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    # use: `python -m uvicorn main:app --reload --app-dir src`
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

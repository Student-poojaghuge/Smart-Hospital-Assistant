from fastapi import FastAPI
from backend.routes import auth
from backend.routes import patients
from backend.routes import health_assessment
from backend.routes import doctors
from backend.routes import appointments
app = FastAPI(
    title="Smart Hospital Assistant API",
    version="1.0.0"
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(health_assessment.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
@app.get("/")
def home():
    return {
        "message": "Smart Hospital Assistant API is running"
    }